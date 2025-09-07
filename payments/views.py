import stripe
import json
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Course
from .models import Order, OrderItem, Payment
from .serializers import (
    OrderSerializer, OrderCreateSerializer, PaymentSerializer,
    CheckoutSerializer, CourseOrderSerializer
)

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payment information.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments to show only user's own payments"""
        return Payment.objects.filter(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling orders and payments for various content types.
    Provides endpoints for:
    - Creating orders with multiple items
    - Processing payments
    - Viewing order history
    - Downloading receipts
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Filter orders to show only user's own orders"""
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items', 'payment'
        ).order_by('-created_at')
    
    @action(detail=False)
    def history(self, request):
        """
        Get user's order history with details
        """
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def receipt(self, request, pk=None):
        """
        Generate and return payment receipt
        """
        order = self.get_object()
        if order.status != 'completed':
            return Response(
                {'error': 'Receipt only available for completed orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get items
        items = order.items.all()
        item_details = []
        
        for item in items:
            item_details.append({
                'name': item.name,
                'description': item.description,
                'quantity': item.quantity,
                'price': str(item.price),
                'subtotal': str(item.subtotal)
            })
        
        # Basic receipt data
        receipt_data = {
            'order_id': order.id,
            'date': order.created_at.strftime('%Y-%m-%d'),
            'completed_date': order.completed_at.strftime('%Y-%m-%d') if order.completed_at else None,
            'items': item_details,
            'subtotal': str(order.subtotal),
            'discount': str(order.discount_amount),
            'tax': str(order.tax_amount),
            'total': str(order.total_amount),
            'status': order.status
        }
        
        # Add payment details if available
        if order.payment:
            receipt_data['payment'] = {
                'id': order.payment.id,
                'method': order.payment.payment_method,
                'provider': order.payment.provider,
                'transaction_id': order.payment.transaction_id,
                'receipt_url': order.payment.receipt_url
            }
            
        return Response(receipt_data)
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def legacy_course_order(self, request):
        """
        Legacy endpoint for direct course purchases (backward compatibility)
        """
        serializer = CourseOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get course
        course_id = serializer.validated_data['course_id']
        course = get_object_or_404(Course, id=course_id)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            course=course,  # Legacy support
            status='draft',
            subtotal=course.price,
            total_amount=course.price
        )
        
        # Get ContentType for course
        content_type = ContentType.objects.get_for_model(Course)
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            content_type=content_type,
            object_id=course.id,
            name=course.title,
            description=course.description,
            price=course.price,
            quantity=1
        )
        
        # Return order data for checkout
        order_serializer = OrderSerializer(order)
        return Response({
            'order': order_serializer.data,
            'message': 'Order created, proceed to checkout'
        })


class CheckoutView(generics.GenericAPIView):
    """
    Process payment checkout for an order
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer
    
    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the order
        order_id = serializer.validated_data['order_id']
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order is already in progress
        if order.status != 'draft':
            return Response({
                'error': 'Order is already being processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get payment method and details
        payment_method = serializer.validated_data['payment_method']
        payment_details = serializer.validated_data.get('payment_details', {})
        
        try:
            # Create payment object
            payment = Payment.objects.create(
                user=request.user,
                amount=order.total_amount,
                currency='eur',
                payment_method=payment_method,
                payment_details=payment_details,
                status='pending',
                provider='stripe'
            )
            
            # Associate payment with order
            order.payment = payment
            order.status = 'pending_payment'
            order.save()
            
            # Create Stripe PaymentIntent
            metadata = {
                'order_id': str(order.id),
                'user_id': str(request.user.id)
            }
            
            # Add item details to metadata
            items_meta = []
            for item in order.items.all():
                items_meta.append(f"{item.content_type.model}:{item.object_id}")
            
            if items_meta:
                metadata['items'] = json.dumps(items_meta)
            
            intent = stripe.PaymentIntent.create(
                amount=payment.amount_in_cents,
                currency=payment.currency,
                metadata=metadata,
                payment_method_types=['card']
            )
            
            # Update payment with Stripe details
            payment.provider_payment_id = intent.id
            payment.provider_reference = intent.id
            payment.save()
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_id': payment.id,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                'order': OrderSerializer(order).data
            })
            
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PaymentConfirmView(generics.GenericAPIView):
    """
    Confirm payment and complete order
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, payment_id):
        # Get payment
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # Get associated order
        try:
            order = payment.order
        except Order.DoesNotExist:
            return Response({
                'error': 'No order associated with this payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify payment with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(
                payment.provider_payment_id
            )
            
            if payment_intent.status == 'succeeded':
                # Mark payment as completed
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                
                # Set receipt URL if available
                if hasattr(payment_intent, 'charges') and payment_intent.charges.data:
                    charge = payment_intent.charges.data[0]
                    if hasattr(charge, 'receipt_url'):
                        payment.receipt_url = charge.receipt_url
                
                payment.save()
                
                # Complete order and create enrollments
                order.mark_as_completed()
                
                return Response({
                    'status': 'success',
                    'message': 'Payment confirmed and enrollments created'
                })
            else:
                return Response({
                    'error': f'Payment not completed: {payment_intent.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, payment_id):
        """
        Check payment status
        """
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(
                payment.provider_payment_id
            )
            
            return Response({
                'status': payment_intent.status,
                'payment': PaymentSerializer(payment).data
            })
            
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
