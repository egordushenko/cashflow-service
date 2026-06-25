"""URL configuration for cashflow_service project."""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cashflow.api import (
    CashFlowRecordViewSet,
    CategoryViewSet,
    OperationTypeViewSet,
    StatusViewSet,
    SubcategoryViewSet,
)

router = DefaultRouter()
router.register('statuses', StatusViewSet, basename='status')
router.register('types', OperationTypeViewSet, basename='type')
router.register('categories', CategoryViewSet, basename='category')
router.register('subcategories', SubcategoryViewSet, basename='subcategory')
router.register('records', CashFlowRecordViewSet, basename='record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('cashflow.urls')),
]
