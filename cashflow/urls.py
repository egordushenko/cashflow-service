from django.urls import path

from . import views

app_name = 'cashflow'

urlpatterns = [
    # Записи ДДС
    path('', views.record_list, name='record_list'),
    path('records/create/', views.record_create, name='record_create'),
    path('records/<int:pk>/edit/', views.record_edit, name='record_edit'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'),

    # Справочники
    path('references/', views.references, name='references'),

    path('references/status/create/', views.status_create, name='status_create'),
    path('references/status/<int:pk>/edit/', views.status_edit, name='status_edit'),
    path('references/status/<int:pk>/delete/', views.status_delete, name='status_delete'),

    path('references/type/create/', views.type_create, name='type_create'),
    path('references/type/<int:pk>/edit/', views.type_edit, name='type_edit'),
    path('references/type/<int:pk>/delete/', views.type_delete, name='type_delete'),

    path('references/category/create/', views.category_create, name='category_create'),
    path('references/category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('references/category/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('references/subcategory/create/', views.subcategory_create, name='subcategory_create'),
    path('references/subcategory/<int:pk>/edit/', views.subcategory_edit, name='subcategory_edit'),
    path('references/subcategory/<int:pk>/delete/', views.subcategory_delete, name='subcategory_delete'),

    # AJAX endpoints
    path('ajax/categories/', views.ajax_categories, name='ajax_categories'),
    path('ajax/subcategories/', views.ajax_subcategories, name='ajax_subcategories'),
]
