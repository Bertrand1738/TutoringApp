"""
Models for managing different content types for enrollment.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

class ContentType(models.Model):
    """
    Different types of purchasable content
    """
    TYPE_CHOICES = [
        ('course', 'Full Course'),
        ('video', 'Individual Video'),
        ('live_session', 'Live Session'),
        ('bundle', 'Content Bundle'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Generic foreign key to the actual content object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # If this is a bundle, it can contain multiple content items
    is_bundle = models.BooleanField(default=False)
    
    # Discount information
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    @property
    def discount_amount(self):
        """Calculate discount amount if applicable"""
        if self.original_price and self.price:
            return self.original_price - self.price
        return None
    
    @property
    def has_discount(self):
        """Check if this content has a discount"""
        return self.original_price is not None and self.price < self.original_price


class ContentBundle(models.Model):
    """
    A bundle of multiple content items (courses, videos, sessions)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Items in this bundle
    content_items = models.ManyToManyField(
        ContentType, 
        related_name='bundles'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def item_count(self):
        """Get number of items in bundle"""
        return self.content_items.count()
    
    @property
    def savings_amount(self):
        """Calculate savings compared to buying items individually"""
        if not self.original_price:
            total_individual_price = sum(item.price for item in self.content_items.all())
            return total_individual_price - self.price
        return self.original_price - self.price
    
    @property
    def savings_percentage(self):
        """Calculate savings percentage"""
        if not self.original_price:
            total_individual_price = sum(item.price for item in self.content_items.all())
            if total_individual_price > 0:
                return int((total_individual_price - self.price) / total_individual_price * 100)
            return 0
        
        if self.original_price > 0:
            return int((self.original_price - self.price) / self.original_price * 100)
        return 0
