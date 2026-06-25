from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Status(models.Model):
    """Статус записи ДДС (например: Бизнес, Личное, Налог)."""

    name = models.CharField('Название', max_length=255, unique=True)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['name']

    def __str__(self):
        return self.name


class OperationType(models.Model):
    """Тип операции (Пополнение / Списание)."""

    name = models.CharField('Название', max_length=255, unique=True)

    class Meta:
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категория, привязанная к конкретному типу операции."""

    name = models.CharField('Название', max_length=255)
    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.PROTECT,
        related_name='categories',
        verbose_name='Тип операции',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['operation_type__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'operation_type'],
                name='unique_category_name_per_operation_type',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.operation_type.name})'


class Subcategory(models.Model):
    """Подкатегория, привязанная к конкретной категории."""

    name = models.CharField('Название', max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='subcategories',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_subcategory_name_per_category',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.category.name})'


class CashFlowRecord(models.Model):
    """Запись о движении денежных средств (ДДС)."""

    created_date = models.DateField('Дата', default=date.today)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='Статус',
    )
    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='Тип операции',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='Категория',
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='Подкатегория',
    )
    amount = models.DecimalField(
        'Сумма, ₽',
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ['-created_date', '-id']

    def __str__(self):
        return f'{self.created_date} — {self.operation_type} — {self.amount} ₽'
