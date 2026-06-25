from decimal import Decimal

from rest_framework import serializers

from .models import Category, CashFlowRecord, OperationType, Status, Subcategory


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class OperationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationType
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'operation_type']


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']


class CashFlowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlowRecord
        fields = [
            'id',
            'created_date',
            'status',
            'operation_type',
            'category',
            'subcategory',
            'amount',
            'comment',
        ]

    def validate_amount(self, value):
        if value is None or value <= Decimal('0'):
            raise serializers.ValidationError('Сумма должна быть больше 0.')
        return value

    def validate(self, attrs):
        # Учитываем partial update: берём значения из attrs либо из instance.
        instance = self.instance
        operation_type = attrs.get(
            'operation_type', getattr(instance, 'operation_type', None)
        )
        category = attrs.get('category', getattr(instance, 'category', None))
        subcategory = attrs.get('subcategory', getattr(instance, 'subcategory', None))

        if operation_type and category and category.operation_type_id != operation_type.id:
            raise serializers.ValidationError(
                {'category': 'Категория не относится к выбранному типу операции.'}
            )

        if category and subcategory and subcategory.category_id != category.id:
            raise serializers.ValidationError(
                {'subcategory': 'Подкатегория не относится к выбранной категории.'}
            )

        return attrs
