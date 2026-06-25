from django.contrib import admin

from .models import Category, CashFlowRecord, OperationType, Status, Subcategory


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'operation_type']
    list_filter = ['operation_type']
    search_fields = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']
    list_filter = ['category', 'category__operation_type']
    search_fields = ['name']


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'created_date',
        'status',
        'operation_type',
        'category',
        'subcategory',
        'amount',
    ]
    list_filter = ['status', 'operation_type', 'category', 'subcategory', 'created_date']
    search_fields = ['comment']
    date_hierarchy = 'created_date'
