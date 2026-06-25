# Cashflow Service — учёт движения денежных средств (ДДС)

Веб-сервис на Django для учёта движения денежных средств: создание,
просмотр, редактирование и удаление записей ДДС, а также управление
справочниками (статусы, типы операций, категории, подкатегории) с
соблюдением логических зависимостей между сущностями.

## Краткое описание

Пользователь ведёт записи о доходах и расходах. Каждая запись связана со
статусом, типом операции, категорией и подкатегорией. Система не позволяет
выбрать категорию, не относящуюся к типу операции, или подкатегорию, не
относящуюся к категории — валидация работает и на клиенте (зависимые
select-поля через AJAX), и на сервере (формы и DRF-сериализаторы).

## Возможности

- Таблица всех записей ДДС на главной странице.
- Фильтры по периоду дат, статусу, типу, категории и подкатегории (GET-параметры, комбинируются, значения сохраняются).
- CRUD записей ДДС через веб-интерфейс с подтверждением удаления.
- Страница справочников: управление статусами, типами, категориями и подкатегориями на одной странице.
- Зависимые select-поля: категории зависят от типа, подкатегории — от категории.
- Защита справочников от удаления, если они используются в записях (`on_delete=PROTECT`, без silent cascade).
- Серверная и клиентская валидация бизнес-правил.
- REST API (DRF) для всех сущностей с теми же проверками зависимостей.
- Django admin для всех моделей.
- Management-команда `seed_data` для начального заполнения.
- Unit-тесты.

## Стек

- Python 3.11+
- Django 5.2
- Django REST Framework 3.x
- SQLite (по умолчанию)
- Django Templates + Bootstrap 5 (CDN)
- Минимальный ванильный JavaScript для зависимых select-полей

## Как запустить локально

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows (PowerShell/CMD)

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Приложение будет доступно на http://127.0.0.1:8000/

## База и тестовые данные

```bash
python manage.py migrate       # создать схему БД
python manage.py seed_data     # справочники + примеры записей ДДС
```

Команда `seed_data` создаёт статусы (Бизнес, Личное, Налог), типы
(Пополнение, Списание), полное дерево категорий/подкатегорий из ТЗ и
несколько примеров записей, чтобы главная страница не была пустой.
Команда идемпотентна для справочников (`get_or_create`); примеры записей
создаются только если записей ещё нет.

Создание администратора (опционально, для `/admin/`):

```bash
python manage.py createsuperuser
```

## Как запустить тесты

```bash
python manage.py test
```

Покрывают: создание валидной записи, запрет `amount <= 0`, запрет
неверной связки тип/категория и категория/подкатегория, обязательные
поля, открытие главной страницы, работу фильтра по типу, AJAX-эндпоинты,
ответ API и отклонение неверных связок через API.

## Доступные страницы

| URL                          | Назначение                                   |
|------------------------------|----------------------------------------------|
| `/`                          | Список записей ДДС с фильтрами               |
| `/records/create/`           | Создание записи                              |
| `/records/<id>/edit/`        | Редактирование записи                        |
| `/records/<id>/delete/`      | Подтверждение удаления записи                |
| `/references/`               | Справочники (4 блока на одной странице)      |
| `/admin/`                    | Django admin                                  |

CRUD справочников: `/references/<status|type|category|subcategory>/create/`,
`.../<id>/edit/`, `.../<id>/delete/`.

AJAX-эндпоинты для зависимых списков:

- `GET /ajax/categories/?operation_type=<id>` → `[{"id":..,"name":..}, ...]`
- `GET /ajax/subcategories/?category=<id>` → `[{"id":..,"name":..}, ...]`

## API endpoints (DRF)

Корень API: `/api/` (доступен браузерный DRF-интерфейс).

| URL                  | Сущность        |
|----------------------|-----------------|
| `/api/statuses/`     | Status          |
| `/api/types/`        | OperationType   |
| `/api/categories/`   | Category (фильтр `?operation_type=<id>`) |
| `/api/subcategories/`| Subcategory (фильтр `?category=<id>`) |
| `/api/records/`      | CashFlowRecord  |

Все viewset-ы — `ModelViewSet`. Для `CashFlowRecord` сериализатор
проверяет: `amount > 0`, `category.operation_type == operation_type`,
`subcategory.category == category`.

## Структура проекта

```
cashflow_service/      # настройки проекта, корневой urls.py (admin + api + cashflow)
cashflow/
  models.py            # Status, OperationType, Category, Subcategory, CashFlowRecord
  forms.py             # ModelForm + бизнес-валидация в clean()
  views.py             # web-вьюхи + AJAX endpoints
  urls.py              # маршруты приложения
  serializers.py       # DRF-сериализаторы
  api.py               # DRF ModelViewSet-ы
  admin.py             # регистрация моделей в admin
  tests.py             # unit-тесты
  management/commands/seed_data.py
  templates/cashflow/  # Bootstrap-шаблоны
  static/cashflow/js/  # dependent_selects.js
```

## Скриншоты

_Раздел-заготовка — добавьте скриншоты главной страницы, формы записи и
страницы справочников._
