from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .forms import CashFlowRecordForm
from .models import Category, CashFlowRecord, OperationType, Status, Subcategory


class BaseFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status = Status.objects.create(name='Бизнес')
        cls.spend = OperationType.objects.create(name='Списание')
        cls.income = OperationType.objects.create(name='Пополнение')

        cls.cat_infra = Category.objects.create(name='Инфраструктура', operation_type=cls.spend)
        cls.cat_sales = Category.objects.create(name='Продажи', operation_type=cls.income)

        cls.sub_vps = Subcategory.objects.create(name='VPS', category=cls.cat_infra)
        cls.sub_subs = Subcategory.objects.create(name='Подписки', category=cls.cat_sales)

    def base_data(self, **overrides):
        data = {
            'created_date': '2026-06-25',
            'status': self.status.id,
            'operation_type': self.spend.id,
            'category': self.cat_infra.id,
            'subcategory': self.sub_vps.id,
            'amount': '1500.00',
            'comment': 'тест',
        }
        data.update(overrides)
        return data


class CashFlowRecordFormTests(BaseFixtures):
    def test_valid_record_creates(self):
        form = CashFlowRecordForm(data=self.base_data())
        self.assertTrue(form.is_valid(), form.errors)
        record = form.save()
        self.assertEqual(CashFlowRecord.objects.count(), 1)
        self.assertEqual(record.amount, Decimal('1500.00'))

    def test_amount_must_be_positive(self):
        form = CashFlowRecordForm(data=self.base_data(amount='0'))
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_negative_amount_rejected(self):
        form = CashFlowRecordForm(data=self.base_data(amount='-100'))
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_category_must_match_operation_type(self):
        # cat_sales принадлежит типу "Пополнение", а тип = "Списание"
        form = CashFlowRecordForm(
            data=self.base_data(category=self.cat_sales.id, subcategory=self.sub_subs.id)
        )
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_subcategory_must_match_category(self):
        # sub_subs принадлежит cat_sales, а категория = cat_infra
        form = CashFlowRecordForm(data=self.base_data(subcategory=self.sub_subs.id))
        self.assertFalse(form.is_valid())
        self.assertIn('subcategory', form.errors)

    def test_required_fields(self):
        form = CashFlowRecordForm(data={'created_date': '2026-06-25'})
        self.assertFalse(form.is_valid())
        for field in ('amount', 'operation_type', 'category', 'subcategory', 'status'):
            self.assertIn(field, form.errors)


class ViewTests(BaseFixtures):
    def test_record_list_opens(self):
        resp = self.client.get(reverse('cashflow:record_list'))
        self.assertEqual(resp.status_code, 200)

    def test_record_list_empty_text(self):
        resp = self.client.get(reverse('cashflow:record_list'))
        self.assertContains(resp, 'Записей пока нет')

    def test_create_record_via_view(self):
        resp = self.client.post(
            reverse('cashflow:record_create'), data=self.base_data()
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CashFlowRecord.objects.count(), 1)

    def test_filter_by_operation_type(self):
        CashFlowRecord.objects.create(
            created_date=date(2026, 6, 25), status=self.status,
            operation_type=self.spend, category=self.cat_infra,
            subcategory=self.sub_vps, amount=Decimal('100'),
        )
        CashFlowRecord.objects.create(
            created_date=date(2026, 6, 25), status=self.status,
            operation_type=self.income, category=self.cat_sales,
            subcategory=self.sub_subs, amount=Decimal('200'),
        )
        resp = self.client.get(
            reverse('cashflow:record_list'), {'operation_type': self.income.id}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['records']), 1)
        self.assertEqual(resp.context['records'][0].operation_type, self.income)

    def test_protected_reference_delete(self):
        CashFlowRecord.objects.create(
            created_date=date(2026, 6, 25), status=self.status,
            operation_type=self.spend, category=self.cat_infra,
            subcategory=self.sub_vps, amount=Decimal('100'),
        )
        resp = self.client.post(
            reverse('cashflow:status_delete', args=[self.status.id]), follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Status.objects.filter(pk=self.status.id).exists())


class AjaxTests(BaseFixtures):
    def test_ajax_categories(self):
        resp = self.client.get(
            reverse('cashflow:ajax_categories'), {'operation_type': self.spend.id}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Инфраструктура')

    def test_ajax_subcategories(self):
        resp = self.client.get(
            reverse('cashflow:ajax_subcategories'), {'category': self.cat_infra.id}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'VPS')


class ApiTests(BaseFixtures):
    def test_api_records_list(self):
        resp = self.client.get('/api/records/')
        self.assertEqual(resp.status_code, 200)

    def test_api_rejects_wrong_category_type(self):
        payload = {
            'created_date': '2026-06-25',
            'status': self.status.id,
            'operation_type': self.spend.id,
            'category': self.cat_sales.id,  # неверный тип
            'subcategory': self.sub_subs.id,
            'amount': '100.00',
        }
        resp = self.client.post('/api/records/', data=payload, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('category', resp.json())

    def test_api_rejects_wrong_subcategory(self):
        payload = {
            'created_date': '2026-06-25',
            'status': self.status.id,
            'operation_type': self.spend.id,
            'category': self.cat_infra.id,
            'subcategory': self.sub_subs.id,  # неверная категория
            'amount': '100.00',
        }
        resp = self.client.post('/api/records/', data=payload, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('subcategory', resp.json())

    def test_api_rejects_non_positive_amount(self):
        payload = {
            'created_date': '2026-06-25',
            'status': self.status.id,
            'operation_type': self.spend.id,
            'category': self.cat_infra.id,
            'subcategory': self.sub_vps.id,
            'amount': '0',
        }
        resp = self.client.post('/api/records/', data=payload, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('amount', resp.json())
