"""
Views for assignments and submissions
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max

from courses.assignment_models import Assignment, Submission, AssignmentFeedback
from courses.assignment_serializers import (
    AssignmentSerializer, 
    SubmissionSerializer, 
    AssignmentFeedbackSerializer
)
from courses.models import Course
from core.permissions import IsEnrolledOrTeacher, IsTeacherOrReadOnly, IsTeacher


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for assignments
    
    list:
        Get all assignments in a course
        
    retrieve:
        Get a specific assignment
        
    create:
        Create a new assignment (teachers only)
        
    update:
        Update an assignment (teachers only)
        
    destroy:
        Delete an assignment (teachers only)
    """
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_queryset(self):
        """
        Filter assignments based on:
        1. Course ID if provided
        2. User's role (teacher sees all, student sees available assignments)
        """
        # Get course_pk from URL if available
        course_pk = self.kwargs.get('course_pk')
        
        # Base queryset
        queryset = Assignment.objects.select_related('course')
        
        # Filter by course if specified
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
            
        # Filter based on user role and enrollment
        user = self.request.user
        
        # Check if user is a teacher
        is_teacher = hasattr(user, 'teacher_profile')
        
        if is_teacher:
            # Teachers see all assignments for courses they teach
            return queryset.filter(course__teacher=user.teacher_profile)
        else:
            # Students see:
            # 1. Preview assignments for all published courses
            # 2. All assignments for courses they're enrolled in
            now = timezone.now()
            return queryset.filter(
                Q(is_preview=True, course__published=True) |
                Q(course__enrolled_students__student=user, available_from__lte=now)
            ).distinct()
    
    def perform_create(self, serializer):
        """Set course from URL if provided, otherwise use the one in the data"""
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            serializer.save(course=course)
        else:
            serializer.save()
            
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None, course_pk=None):
        """Get all submissions for an assignment (teachers only)"""
        assignment = self.get_object()
        
        # Only teachers can see all submissions
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {'detail': 'Only teachers can view all submissions.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Ensure teacher owns the course
        if assignment.course.teacher != request.user.teacher_profile:
            return Response(
                {'detail': 'You do not have permission to view these submissions.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        submissions = Submission.objects.filter(assignment=assignment)
        serializer = SubmissionSerializer(
            submissions, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def my_submission(self, request, pk=None, course_pk=None):
        """Get the current user's submission for this assignment"""
        assignment = self.get_object()
        
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()
        
        if not submission:
            return Response(
                {'detail': 'You have not submitted anything for this assignment yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = SubmissionSerializer(
            submission,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None, course_pk=None):
        """Get statistics for an assignment (teachers only)"""
        assignment = self.get_object()
        
        # Only teachers can see statistics
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {'detail': 'Only teachers can view assignment statistics.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Ensure teacher owns the course
        if assignment.course.teacher != request.user.teacher_profile:
            return Response(
                {'detail': 'You do not have permission to view these statistics.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get submission stats
        total_students = assignment.course.enrolled_students.count()
        submission_count = Submission.objects.filter(assignment=assignment).count()
        graded_count = Submission.objects.filter(
            assignment=assignment,
            status='graded'
        ).count()
        
        # Calculate average score for graded submissions
        average_score = Submission.objects.filter(
            assignment=assignment,
            status='graded',
            points_earned__isnull=False
        ).aggregate(avg_score=Avg('points_earned'))['avg_score'] or 0
        
        # Calculate percentage of students who've submitted
        submission_rate = (submission_count / total_students * 100) if total_students > 0 else 0
        
        return Response({
            'total_students': total_students,
            'submission_count': submission_count,
            'graded_count': graded_count,
            'submission_rate': round(submission_rate, 1),
            'average_score': round(average_score, 1),
            'max_points': assignment.max_points,
            'average_percent': round(average_score / assignment.max_points * 100, 1) if assignment.max_points > 0 else 0,
        })


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for submissions
    
    list:
        Get all submissions (teachers see submissions for their courses,
        students see their own submissions)
        
    retrieve:
        Get a specific submission
        
    create:
        Submit an assignment
        
    update:
        Update a submission (only allowed before grading)
        
    grade:
        Grade a submission (teachers only)
    """
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter submissions based on user role"""
        user = self.request.user
        
        # Check if user is a teacher
        is_teacher = hasattr(user, 'teacher_profile')
        
        if is_teacher:
            # Teachers see submissions for courses they teach
            return Submission.objects.filter(
                assignment__course__teacher=user.teacher_profile
            )
        else:
            # Students see only their own submissions
            return Submission.objects.filter(student=user)
    
    def get_permissions(self):
        """
        - Only enrolled students can submit
        - Only teachers can grade
        - Students can update their own submissions
        """
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsEnrolledOrTeacher()]
        elif self.action in ['grade', 'feedback']:
            return [permissions.IsAuthenticated(), IsTeacher()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Set assignment from URL if provided"""
        assignment_pk = self.kwargs.get('assignment_pk')
        if assignment_pk:
            assignment = get_object_or_404(Assignment, pk=assignment_pk)
            serializer.save(assignment=assignment)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsTeacher])
    def grade(self, request, pk=None):
        """Grade a submission"""
        submission = self.get_object()
        
        # Ensure the teacher owns the course
        if submission.assignment.course.teacher != request.user.teacher_profile:
            return Response(
                {'detail': 'You do not have permission to grade this submission.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get points earned from request data
        if 'points_earned' not in request.data:
            return Response(
                {'detail': 'Points earned is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        points = int(request.data['points_earned'])
        if points < 0 or points > submission.assignment.max_points:
            return Response(
                {'detail': f'Points must be between 0 and {submission.assignment.max_points}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update submission
        submission.points_earned = points
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.status = 'graded'
        submission.save()
        
        # Add feedback if provided
        if 'feedback' in request.data:
            feedback_data = {
                'submission': submission.id,
                'comment': request.data['feedback'],
            }
            
            feedback_serializer = AssignmentFeedbackSerializer(
                data=feedback_data,
                context={'request': request}
            )
            
            if feedback_serializer.is_valid():
                feedback_serializer.save()
        
        serializer = SubmissionSerializer(submission, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        """Get feedback for a submission"""
        submission = self.get_object()
        
        # Students can only see feedback for their own submissions
        if not hasattr(request.user, 'teacher_profile') and submission.student != request.user:
            return Response(
                {'detail': 'You do not have permission to view this feedback.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        feedback = AssignmentFeedback.objects.filter(submission=submission)
        serializer = AssignmentFeedbackSerializer(
            feedback, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoints for assignment feedback
    
    list:
        Get all feedback for a submission
        
    retrieve:
        Get specific feedback
        
    create:
        Add feedback to a submission (teachers only)
        
    update:
        Update feedback (teachers only, own feedback only)
        
    destroy:
        Delete feedback (teachers only, own feedback only)
    """
    serializer_class = AssignmentFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        """Filter feedback based on user role"""
        user = self.request.user
        
        # Get submission_pk from URL if available
        submission_pk = self.kwargs.get('submission_pk')
        
        # Base queryset
        queryset = AssignmentFeedback.objects.select_related(
            'submission', 'submission__assignment', 'submission__student', 'teacher'
        )
        
        # Filter by submission if specified
        if submission_pk:
            queryset = queryset.filter(submission_id=submission_pk)
            
        # Check if user is a teacher
        is_teacher = hasattr(user, 'teacher_profile')
        
        if is_teacher:
            # Teachers see feedback for submissions in their courses
            return queryset.filter(
                submission__assignment__course__teacher=user.teacher_profile
            )
        else:
            # Students see feedback for their submissions
            return queryset.filter(submission__student=user)
    
    def perform_create(self, serializer):
        """Set submission from URL if provided"""
        submission_pk = self.kwargs.get('submission_pk')
        if submission_pk:
            submission = get_object_or_404(Submission, pk=submission_pk)
            
            # Check if teacher owns the course
            if submission.assignment.course.teacher != self.request.user.teacher_profile:
                return Response(
                    {'detail': 'You do not have permission to add feedback to this submission.'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer.save(submission=submission, teacher=self.request.user)
        else:
            serializer.save(teacher=self.request.user)
