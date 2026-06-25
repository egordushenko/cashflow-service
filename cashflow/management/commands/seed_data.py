from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from cashflow.models import (
    Category,
    CashFlowRecord,
    OperationType,
    Status,
    Subcategory,
)


# Структура справочников: тип -> категория -> [подкатегории]
REFERENCE_TREE = {
    'Списание': {
        'Инфраструктура': ['VPS', 'Proxy', 'Домены'],
        'Маркетинг': ['Farpost', 'Avito', 'Telegram Ads'],
        'Зарплаты': ['Разработчики', 'Дизайнеры', 'Менеджеры'],
    },
    'Пополнение': {
        'Продажи': ['Подписки', 'Разовые платежи', 'Дополнительные услуги'],
        'Возврат': ['Возврат от поставщика', 'Возврат комиссии'],
        'Инвестиции': ['Собственные средства', 'Партнёрские средства'],
    },
}

STATUSES = ['Бизнес', 'Личное', 'Налог']


class Command(BaseCommand):
    help = 'Заполняет базу начальными справочниками и примерами записей ДДС.'

    def handle(self, *args, **options):
        statuses = {}
        for name in STATUSES:
            obj, _ = Status.objects.get_or_create(name=name)
            statuses[name] = obj
        self.stdout.write(self.style.SUCCESS(f'Статусы: {len(statuses)}'))

        types = {}
        categories = {}
        subcategories = {}
        for type_name, cats in REFERENCE_TREE.items():
            op_type, _ = OperationType.objects.get_or_create(name=type_name)
            types[type_name] = op_type
            for cat_name, subs in cats.items():
                category, _ = Category.objects.get_or_create(
                    name=cat_name, operation_type=op_type
                )
                categories[(type_name, cat_name)] = category
                for sub_name in subs:
                    sub, _ = Subcategory.objects.get_or_create(
                        name=sub_name, category=category
                    )
                    subcategories[(type_name, cat_name, sub_name)] = sub

        self.stdout.write(
            self.style.SUCCESS(
                f'Типы: {len(types)}, категории: {len(categories)}, '
                f'подкатегории: {len(subcategories)}'
            )
        )

        # Примеры записей ДДС — создаём только если их ещё нет.
        if CashFlowRecord.objects.exists():
            self.stdout.write(
                self.style.WARNING('Записи ДДС уже существуют — пропускаю.')
            )
            return

        today = timezone.localdate()
        samples = [
            ('Списание', 'Инфраструктура', 'VPS', 'Бизнес', '1500.00', 'Аренда VPS на месяц', 0),
            ('Списание', 'Маркетинг', 'Avito', 'Бизнес', '3200.50', 'Размещение объявлений', 1),
            ('Списание', 'Зарплаты', 'Разработчики', 'Бизнес', '120000.00', 'ЗП за июнь', 3),
            ('Пополнение', 'Продажи', 'Подписки', 'Бизнес', '54900.00', 'Оплата подписок', 2),
            ('Пополнение', 'Инвестиции', 'Собственные средства', 'Личное', '200000.00', 'Пополнение оборотных средств', 5),
            ('Пополнение', 'Возврат', 'Возврат комиссии', 'Налог', '780.00', '', 6),
        ]

        created = 0
        for type_name, cat_name, sub_name, status_name, amount, comment, days_ago in samples:
            CashFlowRecord.objects.create(
                created_date=today - timedelta(days=days_ago),
                status=statuses[status_name],
                operation_type=types[type_name],
                category=categories[(type_name, cat_name)],
                subcategory=subcategories[(type_name, cat_name, sub_name)],
                amount=Decimal(amount),
                comment=comment,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано примеров записей ДДС: {created}'))
        self.stdout.write(self.style.SUCCESS('Готово.'))
