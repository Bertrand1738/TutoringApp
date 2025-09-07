from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from courses.models import Course
from decimal import Decimal

class Payment(models.Model):
    """
    Represents a payment for any type of content.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('processing', 'Processing'),
        ('completed', 'Payment Completed'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Payment Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('cancelled', 'Cancelled')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other')
    ]
    
    # Payment information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount"
    )
    currency = models.CharField(max_length=3, default='EUR')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='credit_card'
    )
    payment_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Payment method details"
    )
    
    # Payment processing details
    transaction_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Payment provider information
    provider = models.CharField(
        max_length=20, 
        default='stripe',
        help_text="Payment processor provider"
    )
    provider_payment_id = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Payment ID from provider"
    )
    provider_reference = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Receipt information
    receipt_url = models.URLField(blank=True)
    invoice_id = models.CharField(max_length=50, blank=True)
    
    # Optional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional payment metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.amount} {self.currency}"
    
    @property
    def amount_in_cents(self):
        """Convert amount to cents for payment processors"""
        return int(self.amount * Decimal('100'))
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        from django.utils import timezone
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()


class Order(models.Model):
    """
    Represents an order for courses, videos or other content.
    An order can contain multiple items and is linked to a payment.
    """
    ORDER_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_payment', 'Pending Payment'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    ]
    
    # Order details
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # Legacy support for direct course orders
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name='direct_orders',
        null=True,
        blank=True
    )
    
    # Reference to payment
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order'
    )
    
    # Order status and amounts
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='draft'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Sum of item prices before discounts"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total discount amount"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total tax amount"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Final order amount"
    )
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Discount code
    coupon_code = models.CharField(max_length=50, blank=True)
    
    # Optional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional order metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    
    @property
    def item_count(self):
        """Get number of items in order"""
        return self.items.count()
    
    def calculate_totals(self):
        """Calculate order totals based on items"""
        items = self.items.all()
        self.subtotal = sum(item.price for item in items)
        
        # Apply coupon if exists
        # TODO: Implement coupon handling
        
        # Calculate tax (simplified for now)
        self.tax_amount = Decimal('0.00')
        
        # Final total
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save()
    
    def mark_as_completed(self):
        """
        Mark order as completed and create enrollments
        """
        from django.utils import timezone
        from enrollments.models import Enrollment, VideoEnrollment
        
        if self.status != 'completed':
            # Process each item in the order
            for item in self.items.all():
                # Determine content type
                content_type = item.content_type
                content_object = item.content_object
                
                # Create appropriate enrollment based on content type
                if content_type.model == 'course':
                    # Create course enrollment
                    enrollment = Enrollment.objects.create(
                        student=self.user,
                        course=content_object,
                        status='active',
                        payment=self.payment
                    )
                    
                elif content_type.model == 'video':
                    # Create video enrollment
                    enrollment = Enrollment.objects.create(
                        student=self.user,
                        content_type=content_type,
                        object_id=content_object.id,
                        status='active',
                        payment=self.payment
                    )
                    
                    # Create video-specific enrollment details
                    VideoEnrollment.objects.create(
                        enrollment=enrollment,
                        video=content_object
                    )
                    
                # Add more content types as needed
                
                # Save reference to enrollment in item
                item.enrollment_id = enrollment.id
                item.save(update_fields=['enrollment_id'])
            
            # Update order status
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()


class OrderItem(models.Model):
    """
    Individual item in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Generic foreign key to the content being purchased
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Item details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Reference to created enrollment (set after order completion)
    enrollment_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Optional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True
    )
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.name} (Order {self.order.id})"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.price * self.quantity
    
    @property
    def discount_amount(self):
        """Calculate discount amount if original price exists"""
        if self.original_price:
            return (self.original_price - self.price) * self.quantity
        return Decimal('0.00')
