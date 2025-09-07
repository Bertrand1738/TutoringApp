import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Payment, Order

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle different event types
        if event.type == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event.data.object)
                
        elif event.type == 'payment_intent.payment_failed':
            handle_payment_intent_failed(event.data.object)
            
        elif event.type == 'charge.refunded':
            handle_refund(event.data.object)
            
        # Return success
        return HttpResponse(status=200)
        
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        return HttpResponse(status=400)
        
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        return HttpResponse(status=400)
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=500)


def handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful payment
    """
    try:
        # Find payment by provider_payment_id
        payment = Payment.objects.get(provider_payment_id=payment_intent.id)
        
        # Mark payment as completed
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        
        # Get receipt URL if available
        if hasattr(payment_intent, 'charges') and payment_intent.charges.data:
            charge = payment_intent.charges.data[0]
            if hasattr(charge, 'receipt_url'):
                payment.receipt_url = charge.receipt_url
                
        payment.save()
        
        # Complete order and create enrollments
        if hasattr(payment, 'order'):
            payment.order.mark_as_completed()
            
        logger.info(f"Payment {payment.id} marked as completed via webhook")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for payment_intent: {payment_intent.id}")
        
        # For backward compatibility, try to find order directly
        try:
            # This is for backward compatibility with the old model
            order = Order.objects.get(metadata__stripe_payment_intent_id=payment_intent.id)
            order.mark_as_completed()
            logger.info(f"Legacy order {order.id} marked as completed via webhook")
            
        except Order.DoesNotExist:
            logger.error(f"Order not found for payment_intent: {payment_intent.id}")
            
    except Exception as e:
        logger.error(f"Error processing payment success: {str(e)}")


def handle_payment_intent_failed(payment_intent):
    """
    Handle failed payment
    """
    try:
        payment = Payment.objects.get(provider_payment_id=payment_intent.id)
        payment.status = 'failed'
        payment.save()
        
        # Update order status
        if hasattr(payment, 'order'):
            payment.order.status = 'failed'
            payment.order.save()
            
        logger.info(f"Payment {payment.id} marked as failed via webhook")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for failed payment_intent: {payment_intent.id}")
        
    except Exception as e:
        logger.error(f"Error processing payment failure: {str(e)}")


def handle_refund(charge):
    """
    Handle refund events
    """
    try:
        # Find the payment for this charge's payment intent
        payment_intent_id = charge.payment_intent
        payment = Payment.objects.get(provider_payment_id=payment_intent_id)
        
        # Check if fully or partially refunded
        if charge.refunded:
            payment.status = 'refunded'
        else:
            payment.status = 'partially_refunded'
            
        payment.save()
        
        # Update order if exists
        if hasattr(payment, 'order'):
            payment.order.status = 'refunded'
            payment.order.save()
            
        logger.info(f"Payment {payment.id} marked as refunded via webhook")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for refund of charge: {charge.id}")
        
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
