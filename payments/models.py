from django.db import models
from django.conf import settings
from courses.models import Course
from decimal import Decimal

class Order(models.Model):
    """
    Represents a payment order for a course purchase.
    
    This model tracks the entire payment process from intent creation
    to successful payment and enrollment creation.
    """
    STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('completed', 'Payment Completed'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Payment Refunded')
    ]
    
    # Order details
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,  # Don't delete orders if course is deleted
        related_name='orders'
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in USD"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        help_text="Stripe PaymentIntent ID"
    )
    stripe_payment_method_id = models.CharField(
        max_length=100,
        null=True,
        help_text="Stripe PaymentMethod ID"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional payment/order metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.course.title}"
    
    def mark_as_completed(self):
        """
        Mark order as completed and create enrollment
        """
        if self.status != 'completed':
            from enrollments.models import Enrollment
            
            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=self.user,
                course=self.course
            )
            
            # Update order status
            self.status = 'completed'
            self.metadata['enrollment_id'] = enrollment.id
            self.save()
    
    def mark_as_failed(self, error_message=None):
        """
        Mark order as failed with optional error message
        """
        self.status = 'failed'
        if error_message:
            self.metadata['error'] = error_message
        self.save()

    @property
    def amount_in_cents(self):
        """
        Convert amount to cents for Stripe
        """
        return int(self.amount * Decimal('100'))
