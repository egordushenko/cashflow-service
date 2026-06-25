from rest_framework import viewsets

from .models import Category, CashFlowRecord, OperationType, Status, Subcategory
from .serializers import (
    CashFlowRecordSerializer,
    CategorySerializer,
    OperationTypeSerializer,
    StatusSerializer,
    SubcategorySerializer,
)


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class OperationTypeViewSet(viewsets.ModelViewSet):
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.select_related('operation_type').all()
        operation_type = self.request.query_params.get('operation_type')
        if operation_type:
            qs = qs.filter(operation_type_id=operation_type)
        return qs


class SubcategoryViewSet(viewsets.ModelViewSet):
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        qs = Subcategory.objects.select_related('category').all()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs


class CashFlowRecordViewSet(viewsets.ModelViewSet):
    serializer_class = CashFlowRecordSerializer

    def get_queryset(self):
        return CashFlowRecord.objects.select_related(
            'status', 'operation_type', 'category', 'subcategory'
        ).all()
