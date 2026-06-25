from decimal import Decimal

from django import forms

from .models import Category, CashFlowRecord, OperationType, Status, Subcategory


class CashFlowRecordForm(forms.ModelForm):
    """Форма создания/редактирования записи ДДС с зависимыми select-полями."""

    class Meta:
        model = CashFlowRecord
        fields = [
            'created_date',
            'status',
            'operation_type',
            'category',
            'subcategory',
            'amount',
            'comment',
        ]
        widgets = {
            'created_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d',
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'operation_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_date'].input_formats = ['%Y-%m-%d']
        # amount/operation_type/category/subcategory обязательны
        for name in ('amount', 'operation_type', 'category', 'subcategory', 'status'):
            self.fields[name].required = True

        # Определяем выбранный тип операции / категорию из данных или инстанса,
        # чтобы сузить queryset-ы зависимых полей (серверная защита + удобство).
        op_type_id = self._resolve_id('operation_type')
        category_id = self._resolve_id('category')

        if op_type_id:
            self.fields['category'].queryset = Category.objects.filter(
                operation_type_id=op_type_id
            )
        else:
            self.fields['category'].queryset = Category.objects.none()

        if category_id:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(
                category_id=category_id
            )
        else:
            self.fields['subcategory'].queryset = Subcategory.objects.none()

    def _resolve_id(self, field_name):
        """Достаёт id связанного поля из bound-данных или из instance."""
        if self.is_bound:
            raw = self.data.get(self.add_prefix(field_name))
            if raw:
                try:
                    return int(raw)
                except (TypeError, ValueError):
                    return None
            return None
        value = getattr(self.instance, f'{field_name}_id', None)
        return value

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= Decimal('0'):
            raise forms.ValidationError('Сумма должна быть больше 0.')
        return amount

    def clean(self):
        cleaned = super().clean()
        operation_type = cleaned.get('operation_type')
        category = cleaned.get('category')
        subcategory = cleaned.get('subcategory')

        # Правило: категория должна относиться к выбранному типу операции.
        if operation_type and category and category.operation_type_id != operation_type.id:
            self.add_error(
                'category',
                'Категория не относится к выбранному типу операции.',
            )

        # Правило: подкатегория должна относиться к выбранной категории.
        if category and subcategory and subcategory.category_id != category.id:
            self.add_error(
                'subcategory',
                'Подкатегория не относится к выбранной категории.',
            )

        return cleaned


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}


class OperationTypeForm(forms.ModelForm):
    class Meta:
        model = OperationType
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'operation_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'operation_type': forms.Select(attrs={'class': 'form-select'}),
        }


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
