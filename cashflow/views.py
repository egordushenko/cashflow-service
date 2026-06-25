from django.contrib import messages
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CashFlowRecordForm,
    CategoryForm,
    OperationTypeForm,
    StatusForm,
    SubcategoryForm,
)
from .models import Category, CashFlowRecord, OperationType, Status, Subcategory


# --------------------------------------------------------------------------- #
#  Записи ДДС
# --------------------------------------------------------------------------- #
def record_list(request):
    """Главная страница: таблица записей ДДС с GET-фильтрами."""
    records = CashFlowRecord.objects.select_related(
        'status', 'operation_type', 'category', 'subcategory'
    ).all()

    date_from = request.GET.get('date_from') or ''
    date_to = request.GET.get('date_to') or ''
    status_id = request.GET.get('status') or ''
    operation_type_id = request.GET.get('operation_type') or ''
    category_id = request.GET.get('category') or ''
    subcategory_id = request.GET.get('subcategory') or ''

    if date_from:
        records = records.filter(created_date__gte=date_from)
    if date_to:
        records = records.filter(created_date__lte=date_to)
    if status_id:
        records = records.filter(status_id=status_id)
    if operation_type_id:
        records = records.filter(operation_type_id=operation_type_id)
    if category_id:
        records = records.filter(category_id=category_id)
    if subcategory_id:
        records = records.filter(subcategory_id=subcategory_id)

    # Списки для зависимых select-полей фильтра (сохраняем согласованность).
    categories = Category.objects.all()
    if operation_type_id:
        categories = categories.filter(operation_type_id=operation_type_id)
    subcategories = Subcategory.objects.all()
    if category_id:
        subcategories = subcategories.filter(category_id=category_id)

    context = {
        'records': records,
        'statuses': Status.objects.all(),
        'operation_types': OperationType.objects.all(),
        'categories': categories,
        'subcategories': subcategories,
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'status': status_id,
            'operation_type': operation_type_id,
            'category': category_id,
            'subcategory': subcategory_id,
        },
    }
    return render(request, 'cashflow/record_list.html', context)


def record_create(request):
    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись ДДС успешно создана.')
            return redirect('cashflow:record_list')
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CashFlowRecordForm()
    return render(
        request,
        'cashflow/record_form.html',
        {'form': form, 'title': 'Новая запись ДДС'},
    )


def record_edit(request, pk):
    record = get_object_or_404(CashFlowRecord, pk=pk)
    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись ДДС обновлена.')
            return redirect('cashflow:record_list')
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CashFlowRecordForm(instance=record)
    return render(
        request,
        'cashflow/record_form.html',
        {'form': form, 'title': f'Редактирование записи #{record.pk}'},
    )


def record_delete(request, pk):
    record = get_object_or_404(CashFlowRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Запись ДДС удалена.')
        return redirect('cashflow:record_list')
    return render(
        request,
        'cashflow/record_confirm_delete.html',
        {'record': record},
    )


# --------------------------------------------------------------------------- #
#  Справочники
# --------------------------------------------------------------------------- #
def references(request):
    context = {
        'statuses': Status.objects.all(),
        'operation_types': OperationType.objects.all(),
        'categories': Category.objects.select_related('operation_type').all(),
        'subcategories': Subcategory.objects.select_related('category').all(),
        'status_form': StatusForm(),
        'operation_type_form': OperationTypeForm(),
        'category_form': CategoryForm(),
        'subcategory_form': SubcategoryForm(),
    }
    return render(request, 'cashflow/references.html', context)


# --- Универсальные helpers для CRUD справочников ----------------------------- #
_REFERENCE_CONFIG = {
    'status': (Status, StatusForm, 'Статус'),
    'type': (OperationType, OperationTypeForm, 'Тип операции'),
    'category': (Category, CategoryForm, 'Категория'),
    'subcategory': (Subcategory, SubcategoryForm, 'Подкатегория'),
}


def _reference_create(request, kind):
    model, form_cls, label = _REFERENCE_CONFIG[kind]
    if request.method == 'POST':
        form = form_cls(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'{label}: запись добавлена.')
        else:
            errors = '; '.join(
                f'{field}: {", ".join(errs)}' for field, errs in form.errors.items()
            )
            messages.error(request, f'{label}: ошибка. {errors}')
    return redirect('cashflow:references')


def _reference_edit(request, kind, pk):
    model, form_cls, label = _REFERENCE_CONFIG[kind]
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_cls(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{label}: запись обновлена.')
            return redirect('cashflow:references')
        messages.error(request, f'{label}: исправьте ошибки в форме.')
    else:
        form = form_cls(instance=obj)
    return render(
        request,
        'cashflow/reference_form.html',
        {'form': form, 'title': f'Редактирование: {label}', 'obj': obj},
    )


def _reference_delete(request, kind, pk):
    model, form_cls, label = _REFERENCE_CONFIG[kind]
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, f'{label}: запись удалена.')
        except ProtectedError:
            messages.error(
                request,
                f'{label} «{obj}» используется в других записях и не может быть удалён.',
            )
        return redirect('cashflow:references')
    return render(
        request,
        'cashflow/reference_confirm_delete.html',
        {'obj': obj, 'label': label, 'kind': kind},
    )


# Тонкие именованные обёртки для маршрутов
def status_create(request):
    return _reference_create(request, 'status')


def status_edit(request, pk):
    return _reference_edit(request, 'status', pk)


def status_delete(request, pk):
    return _reference_delete(request, 'status', pk)


def type_create(request):
    return _reference_create(request, 'type')


def type_edit(request, pk):
    return _reference_edit(request, 'type', pk)


def type_delete(request, pk):
    return _reference_delete(request, 'type', pk)


def category_create(request):
    return _reference_create(request, 'category')


def category_edit(request, pk):
    return _reference_edit(request, 'category', pk)


def category_delete(request, pk):
    return _reference_delete(request, 'category', pk)


def subcategory_create(request):
    return _reference_create(request, 'subcategory')


def subcategory_edit(request, pk):
    return _reference_edit(request, 'subcategory', pk)


def subcategory_delete(request, pk):
    return _reference_delete(request, 'subcategory', pk)


# --------------------------------------------------------------------------- #
#  AJAX / JSON endpoints для зависимых списков
# --------------------------------------------------------------------------- #
def ajax_categories(request):
    operation_type = request.GET.get('operation_type')
    qs = Category.objects.all()
    if operation_type:
        qs = qs.filter(operation_type_id=operation_type)
    data = [{'id': c.id, 'name': c.name} for c in qs]
    return JsonResponse(data, safe=False)


def ajax_subcategories(request):
    category = request.GET.get('category')
    qs = Subcategory.objects.all()
    if category:
        qs = qs.filter(category_id=category)
    data = [{'id': s.id, 'name': s.name} for s in qs]
    return JsonResponse(data, safe=False)
