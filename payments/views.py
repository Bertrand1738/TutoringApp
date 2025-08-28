import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Course
from .models import Order
from .serializers import OrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling course orders and Stripe payments.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter orders to show only user's own orders"""
        return Order.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        """
        Create a Stripe PaymentIntent for course purchase
        """
        try:
            # Get course and validate
            course_id = request.data.get('course_id')
            course = get_object_or_404(Course, id=course_id)
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                status='pending'
            )
            
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=order.amount_in_cents,
                currency='usd',
                metadata={
                    'course_id': str(course.id),
                    'order_id': str(order.id)
                }
            )
            
            # Update order with PaymentIntent ID
            order.stripe_payment_intent_id = intent.id
            order.save()
            
            return Response({
                'clientSecret': intent.client_secret,
                'order_id': order.id
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """
        Confirm successful payment and create enrollment
        """
        order = self.get_object()
        
        try:
            # Verify payment with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(
                order.stripe_payment_intent_id
            )
            
            if payment_intent.status == 'succeeded':
                # Mark order complete and create enrollment
                order.mark_as_completed()
                return Response({'status': 'success'})
            else:
                return Response(
                    {'error': 'Payment not completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
