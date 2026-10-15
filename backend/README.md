# BizMind Backend Service

> **Модуль:** Аналитический бэкенд и API-шлюз платформы BizMind  
> **Версия:** 1.0.0  
> **Стек:** Python 3.12, FastAPI, SQLAlchemy 2.0 (ORM), Pydantic v2, SQLite / PostgreSQL, openpyxl, pandas, pytest, uv

---

## 1. Назначение и архитектурные принципы

Бэкенд BizMind предоставляет REST API для оперативного управления закупками, складскими остатками и финансами предприятий малого бизнеса (HoReCa и ритейл).

### Ключевые архитектурные принципы:
1. **Детерминированная аналитика без непрозрачного AI:** все расчёты скачков цен, потенциальной экономии, среднесуточного потребления сырья и прогноза истощения остатков производятся программными математическими алгоритмами на стороне сервера.
2. **Строгая мультитенантность (Multi-Tenancy):** изоляция данных на уровне каждой строки базы данных через обязательную привязку к `organization_id`.
3. **Бесшовная передача тенанта через HTTP-заголовки:** клиент отправляет заголовок `X-Organization-Id: <id>`, валидируемый единой FastAPI-зависимостью `get_current_organization_id`.
4. **Устойчивый импорт Excel/CSV:** устойчивый к вариациям названий колонок парсер таблиц (`openpyxl`, `pandas`) с дедупликацией и отчётом об ошибках.

---

## 2. Структура модуля

```text
backend/
├── src/
│   └── backend/
│       ├── api/                      # Маршруты и HTTP-контроллеры
│       │   ├── auth.py               # Аутентификация, профиль текущего пользователя
│       │   ├── dashboard.py          # Сводные метрики, ключевые алерты, графики
│       │   ├── demo.py               # Сброс базы, скачивание 8 демо-файлов Excel
│       │   ├── deps.py               # Dependency Injection: сессия БД и organization_id
│       │   ├── finances.py           # Операции доходов/расходов и статьи затрат
│       │   ├── forecast.py           # Статистический прогноз истощения запасов
│       │   ├── imports.py            # Загрузка и валидация Excel/CSV
│       │   ├── notifications.py      # Уведомления и статусы прочтения
│       │   ├── purchases.py          # Партии закупок и аудит закупочных цен
│       │   └── suppliers.py          # Контрагенты и сравнение коммерческих офферов
│       ├── demo/                     # Демо-генераторы
│       │   ├── generate_demo_files.py# Генерация 8 бинарных Excel-таблиц (.xlsx)
│       │   └── seed_data.py          # Инициализация и сидирование данных в БД
│       ├── models/
│       │   └── models.py             # SQLAlchemy 2.0 модели сущностей
│       ├── schemas/
│       │   └── schemas.py            # Pydantic v2 схемы валидации DTO
│       ├── services/                 # Сервисный слой бизнес-логики
│       │   ├── comparison_service.py # Расчёт чистой экономии с учётом доставки
│       │   ├── dashboard_service.py  # Сборка KPI и агрегатов для главной страницы
│       │   ├── finance_service.py    # Финансовая статистика, сальдо, фильтрация
│       │   ├── forecast_service.py   # Вычисление суточного расхода и дней до истощения
│       │   ├── import_service.py     # Обработка Excel, нормализация заголовков
│       │   ├── notification_service.py # Формирование и доставка алертов
│       │   └── purchase_service.py   # Детекция скачков цен относительно базы
│       ├── database.py               # Движок SQLAlchemy, SessionLocal, декларативная база
│       └── main.py                   # Инициализация FastAPI, CORS, lifespan
├── tests/
│   └── test_isolation_and_demo.py    # Набор интеграционных тестов изоляции и расчётов
├── Dockerfile                        # Multi-stage сборка Docker-образа
└── pyproject.toml                    # Декларация зависимостей проекта (uv / pip)
```

---

## 3. Модель данных (База данных)

Реляционная схема построена с использованием внешних ключей и каскадного удаления:

```
[ organizations ]
       │ 1
       ├──< [ users ]
       ├──< [ products ] ──< [ purchases ] >── [ suppliers ]
       │          │                   │
       │          └──< [ supplier_offers ] >── [ suppliers ]
       ├──< [ suppliers ]
       ├──< [ financial_transactions ]
       ├──< [ notifications ]
       └──< [ import_batches ]
```

### Основные сущности (`models/models.py`):
1. **Organization:** тенант системы (название, ИИН/БИН, валюта `KZT`).
2. **User:** пользователи организации с ролевой моделью (`owner`, `manager`, `analyst`).
3. **Product:** номенклатурная карточка (наименование, базовая единица измерения, текущий остаток на складе, неснижаемый минимум `min_stock_level`).
4. **Supplier:** поставщик сырья или товаров (контакты, условия доставки, минимальная сумма заказа).
5. **Purchase:** совершённая партия закупки (товар, поставщик, дата, объём, общая сумма, цена за единицу).
6. **SupplierOffer:** предложение из прайс-листа контрагента (цена единицы, мин. объём заказа, стоимость доставки, признак надёжности).
7. **FinancialTransaction:** бухгалтерская операция (доход / расход, категория, сумма, контрагент, описание).
8. **Notification:** аналитическое оповещение (`price_jump`, `alternative_supplier`, `low_stock`, `category_growth`).
9. **ImportBatch:** журнал загрузок файлов Excel/CSV с метаданными и количеством обработанных строк.

---

## 4. Алгоритмы бизнес-аналитики

### 4.1. Детекция скачка закупочных цен (`purchase_service.py`)
Система сравнивает цену единицы товара в последней закупке $P_{last}$ с базовой/предыдущей ценой $P_{prev}$:
$$\Delta P = \frac{P_{last} - P_{prev}}{P_{prev}} \times 100\%$$
Если $\Delta P \ge 5\%$, позиция помечается как инфляционный риск, генерируется алерт в центр уведомлений и выводится в баннер дашборда.

### 4.2. Расчёт чистой экономии альтернативного поставщика (`comparison_service.py`)
Сравнение предложений контрагентов учитывает не только стоимость единицы сырья, но и накладные расходы на логистику:
$$\text{Cost}_{current} = Q \times P_{current} + \text{Delivery}_{current}$$
$$\text{Cost}_{alt} = Q \times P_{alt} + \text{Delivery}_{alt}$$
$$\text{Net Savings} = \text{Cost}_{current} - \text{Cost}_{alt}$$
где $Q$ — объём партии закупки. Если $\text{Net Savings} > 0$ и соблюден минимальный заказ ($Q \ge \text{MOQ}$), формируется рекомендация о смене контрагента.

### 4.3. Прогноз расхода и истощения остатков (`forecast_service.py`)
1. **Период наблюдения:** берётся история закупок за последние $N$ дней (по умолчанию 30 или 90 дней).
2. **Среднесуточное потребление:**
   $$\text{Daily Burn Rate} = \frac{\sum Q_{purchased}}{\text{Days}}$$
3. **Остаток дней до истощения (Runway):**
   $$\text{Days Left} = \frac{\text{Current Stock}}{\text{Daily Burn Rate}}$$
4. **Рекомендуемый заказ на $D$ дней вперед:**
   $$Q_{recommend} = (\text{Daily Burn Rate} \times D) + \text{Min Stock} - \text{Current Stock}$$

---

## 5. API Спецификация (Основные эндпоинты)

| Метод | Путь | Описание | Заголовки |
|---|---|---|---|
| `GET` | `/health` | Liveness-проверка сервиса | — |
| `GET` | `/api/auth/me` | Данные текущего пользователя и организации | `X-Organization-Id` |
| `GET` | `/api/auth/organizations` | Список доступных организаций для входа | — |
| `POST` | `/api/auth/switch-organization` | Переключение рабочего пространства | `X-Organization-Id` |
| `GET` | `/api/dashboard/summary` | Главные метрики, алерт по инфляции, графики | `X-Organization-Id` |
| `GET` | `/api/finances/transactions` | Список финансовых операций с фильтрацией | `X-Organization-Id` |
| `POST` | `/api/finances/transactions` | Создание новой операции | `X-Organization-Id` |
| `GET` | `/api/purchases/` | Журнал закупок и история цен | `X-Organization-Id` |
| `GET` | `/api/suppliers/comparison/{product_id}` | Сравнение цен поставщиков по товару | `X-Organization-Id` |
| `GET` | `/api/forecast/` | Прогноз остатков по всем товарам склада | `X-Organization-Id` |
| `GET` | `/api/notifications/` | Список уведомлений и счетчик непрочитанных | `X-Organization-Id` |
| `POST` | `/api/notifications/{id}/read` | Отметка уведомления как прочитанного | `X-Organization-Id` |
| `POST` | `/api/imports/excel` | Загрузка файла Excel (.xlsx) | `X-Organization-Id` |
| `POST` | `/api/demo/reset-data` | Сброс базы к эталонному демо-состоянию | `X-Organization-Id` |
| `GET` | `/api/demo/download-file/{filename}` | Скачивание демо-файлов Excel | — |

---

## 6. Запуск и разработка

### Локальный запуск через `uv`:
```bash
cd backend
uv sync
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Генерация демонстрационных файлов Excel:
```bash
uv run python -m backend.demo.generate_demo_files
```
Файлы сохраняются в директорию `demo_data/` в корне проекта.

### Запуск автоматических тестов:
```bash
uv run pytest
```
Тестовый набор `tests/test_isolation_and_demo.py` покрывает:
- Корректность сидирования двух тенантов (Cafe Aroma и Daily Cup).
- Изоляцию данных между организациями (запросы для Org 1 не видят записи Org 2).
- Парсинг и импорт Excel с расчетом новых метрик.
- Вычисление разницы цен и экономии.
- Вычисление прогноза остатков.
