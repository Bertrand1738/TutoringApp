from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Payment, Order, OrderItem
from courses.models import Course

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'amount', 'currency', 'payment_method',
            'status', 'provider', 'transaction_id', 'created_at',
            'completed_at', 'receipt_url'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'created_at', 'completed_at',
            'receipt_url', 'provider_payment_id'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'name', 'description', 'quantity', 'price',
            'original_price', 'content_type', 'object_id',
            'content_type_name', 'subtotal'
        ]
        read_only_fields = ['id', 'subtotal']
    
    def get_content_type_name(self, obj):
        return f"{obj.content_type.model}"


class OrderItemCreateSerializer(serializers.Serializer):
    content_type = serializers.CharField(required=True)
    object_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(default=1)
    
    def validate(self, data):
        """
        Validate content_type and object_id combination.
        """
        content_type_name = data.get('content_type')
        object_id = data.get('object_id')
        
        try:
            # Get the Django ContentType
            content_type = ContentType.objects.get(model=content_type_name)
            
            # Get the actual object
            model_class = content_type.model_class()
            content_object = model_class.objects.get(id=object_id)
            
            # Add validated data
            data['content_type_obj'] = content_type
            data['content_object'] = content_object
            
            # Check if the content is purchasable
            if not hasattr(content_object, 'price'):
                raise serializers.ValidationError(
                    f"{content_type_name} with id {object_id} does not have a price attribute"
                )
            
            return data
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"Content type '{content_type_name}' does not exist")
        except model_class.DoesNotExist:
            raise serializers.ValidationError(
                f"{content_type_name} with id {object_id} does not exist"
            )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'subtotal', 'discount_amount',
            'tax_amount', 'total_amount', 'created_at', 'completed_at',
            'items', 'payment_details', 'item_count', 'course'  # Include course for backward compatibility
        ]
        read_only_fields = [
            'id', 'subtotal', 'total_amount', 'created_at',
            'completed_at', 'items', 'payment_details', 'item_count'
        ]
    
    def get_payment_details(self, obj):
        if obj.payment:
            return {
                'id': obj.payment.id,
                'status': obj.payment.status,
                'method': obj.payment.payment_method,
                'created_at': obj.payment.created_at,
                'completed_at': obj.payment.completed_at
            }
        return None
        
    def create(self, validated_data):
        """Add the current user automatically"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, required=True)
    
    class Meta:
        model = Order
        fields = ['items', 'coupon_code']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user
        
        # Create order
        order = Order.objects.create(user=user, **validated_data)
        
        # Create order items
        for item_data in items_data:
            content_type = item_data.pop('content_type_obj')
            content_object = item_data.pop('content_object')
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                content_type=content_type,
                object_id=content_object.id,
                name=getattr(content_object, 'title', 'Untitled'),
                description=getattr(content_object, 'description', ''),
                price=content_object.price,
                original_price=getattr(content_object, 'original_price', None),
                quantity=item_data.get('quantity', 1)
            )
        
        # Calculate order totals
        order.calculate_totals()
        return order


class CheckoutSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        default='credit_card'
    )
    payment_details = serializers.JSONField(required=False, default=dict)
    
    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            if order.status != 'draft':
                raise serializers.ValidationError("Order is not in draft status")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist")


# Legacy serializer for backwards compatibility
class CourseOrderSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
    
    def validate_course_id(self, value):
        try:
            Course.objects.get(id=value)
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist")
