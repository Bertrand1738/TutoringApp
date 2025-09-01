"""
Dashboard views for user accounts.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from enrollments.serializers import EnrollmentSerializer
from payments.serializers import OrderSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_enrollments(request):
    """List all enrollments for the current user"""
    qs = request.user.student_enrollments.select_related("course").order_by("-enrolled_at")
    return Response(EnrollmentSerializer(qs, many=True).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    """List all orders for the current user"""
    qs = request.user.orders.select_related("course").order_by("-created_at")
    return Response(OrderSerializer(qs, many=True).data)
