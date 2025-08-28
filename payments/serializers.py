from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'course',
            'amount',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'created_at',
            'updated_at'
        ]
    
    def create(self, validated_data):
        """Add the current user automatically"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
