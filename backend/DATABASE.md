# 🗄️ Документация базы данных BizMind (Database Architecture & Reference)

Данный документ представляет собой полное техническое руководство по архитектуре данных, моделям SQLAlchemy, связям, правилам целостности и оптимизации базы данных платформы **BizMind**.

---

## 📑 Содержание

1. [Архитектурные принципы и технологии](#-архитектурные-принципы-и-технологии)
2. [Мультитенантность и изоляция данных](#-мультитенантность-и-изоляция-данных)
3. [ER-диаграмма сущностей (Mermaid)](#-er-диаграмма-сущностей-mermaid)
4. [Словарь данных (Data Dictionary — 15 таблиц)](#-словарь-данных-data-dictionary)
   - [1. organizations](#1-organizations-организации-клиенты)
   - [2. users](#2-users-пользователи-и-сотрудники)
   - [3. products](#3-products-товары-и-ингредиенты)
   - [4. suppliers](#4-suppliers-поставщики)
   - [5. supplier_offers](#5-supplier_offers-прайс-лист-и-офферы)
   - [6. offer_price_history](#6-offer_price_history-история-колебания-цен)
   - [7. purchase_orders](#7-purchase_orders-заказы-поставщикам)
   - [8. purchase_order_items](#8-purchase_order_items-позиции-заказов)
   - [9. inventory_movements](#9-inventory_movements-движения-по-складу)
   - [10. purchases](#10-purchases-архив-фактических-закупок)
   - [11. financial_transactions](#11-financial_transactions-финансовые-транзакции)
   - [12. notifications](#12-notifications-уведомления-и-алерты)
   - [13. import_batches](#13-import_batches-пакеты-импорта-данных)
   - [14. activity_logs](#14-activity_logs-журнал-аудита-действий)
   - [15. report_templates](#15-report_templates-шаблоны-конструктора-отчетов)
5. [Жизненные циклы и бизнес-логика (State Machines)](#-жизненные-циклы-и-бизнес-логика)
6. [Миграции и авто-эволюция схемы](#-миграции-и-авто-эволюция-схемы)
7. [Демо-данные и сидирование](#-демо-данные-и-сидирование)
8. [Аналитические запросы и алгоритмы](#-аналитические-запросы-и-алгоритмы)
9. [Персистентность и обслуживание в Docker](#-персистентность-и-обслуживание-в-docker)

---

## 🏛️ Архитектурные принципы и технологии

База данных BizMind спроектирована с учетом гибкости разработки и надежности промышленной эксплуатации:

* **ORM**: [SQLAlchemy 2.0+](https://docs.sqlalchemy.org/) с использованием декларативного маппинга (`Base = declarative_base()`) и строгой типизацией.
* **СУБД по умолчанию (Dev & Embedded)**: **SQLite 3** (`bizmind.db`), оптимизированный под микросервисные развертывания и демо-стенды.
* **Поддержка PostgreSQL**: Подключение настраивается через переменную окружения `DATABASE_URL` (например, `postgresql+psycopg2://user:pass@host:5432/bizmind`).
* **Внешние ключи (Foreign Keys)**: Для SQLite включен обязательный листенер на событие подключения:
  ```python
  @event.listens_for(engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      cursor = dbapi_connection.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()
  ```
  Это гарантирует строгое соблюдение ссылочной целостности (Cascades, Restrict, Set Null) на уровне драйвера.
* **Пул сессий (Session Pool)**: `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)` с автоматическим освобождением сессии в FastAPI-зависимости `get_db()`.

---

## 🏢 Мультитенантность и изоляция данных

BizMind реализует модель **Shared Database, Shared Schema with Row-Level Isolation**:
* Все бизнес-таблицы содержат внешний ключ `organization_id`, ссылающийся на `organizations.id`.
* **Авторизованная фильтрация**: Каждый запрос к API получает текущую организацию через middleware/dependency (`get_current_org_id`) и накладывает условие:
  ```python
  query = db.query(Model).filter(Model.organization_id == current_org_id)
  ```
* **Глобальные сущности (Global Catalog)**:
  * Поставщики из общего маркетплейса имеют `organization_id = NULL`, `is_global = True`, `source_type = "global"`. Они доступны для чтения и сравнения всем арендаторам, но не могут быть случайно удалены или перезаписаны локальными операциями.
  * Системные шаблоны отчетов имеют `organization_id = NULL`, `is_system = True`.

---

## 📊 ER-диаграмма сущностей (Mermaid)

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ USERS : "has members"
    ORGANIZATIONS ||--o{ PRODUCTS : "owns catalog"
    ORGANIZATIONS ||--o{ SUPPLIERS : "owns suppliers"
    ORGANIZATIONS ||--o{ PURCHASE_ORDERS : "issues orders"
    ORGANIZATIONS ||--o{ INVENTORY_MOVEMENTS : "tracks stock"
    ORGANIZATIONS ||--o{ FINANCIAL_TRANSACTIONS : "records cash flow"
    ORGANIZATIONS ||--o{ NOTIFICATIONS : "receives alerts"
    ORGANIZATIONS ||--o{ IMPORT_BATCHES : "imports files"
    ORGANIZATIONS ||--o{ ACTIVITY_LOGS : "audits actions"
    ORGANIZATIONS ||--o{ REPORT_TEMPLATES : "custom templates"

    USERS ||--o{ PURCHASE_ORDERS : "created_by"
    USERS ||--o{ INVENTORY_MOVEMENTS : "registered_by"
    USERS ||--o{ ACTIVITY_LOGS : "performed_by"
    USERS ||--o{ REPORT_TEMPLATES : "authored_by"

    PRODUCTS ||--o{ SUPPLIER_OFFERS : "offered by suppliers"
    PRODUCTS ||--o{ PURCHASE_ORDER_ITEMS : "ordered item"
    PRODUCTS ||--o{ INVENTORY_MOVEMENTS : "stock moved"
    PRODUCTS ||--o{ OFFER_PRICE_HISTORY : "tracks price shifts"
    PRODUCTS ||--o{ NOTIFICATIONS : "triggers alert"
    PRODUCTS ||--o{ PURCHASES : "historical purchases"

    SUPPLIERS ||--o{ SUPPLIER_OFFERS : "publishes offers"
    SUPPLIERS ||--o{ PURCHASE_ORDERS : "fulfills orders"
    SUPPLIERS ||--o{ FINANCIAL_TRANSACTIONS : "payee"
    SUPPLIERS ||--o{ PURCHASES : "historical seller"
    SUPPLIERS ||--o{ OFFER_PRICE_HISTORY : "historical prices"

    SUPPLIER_OFFERS ||--o{ OFFER_PRICE_HISTORY : "price history"

    PURCHASE_ORDERS ||--|{ PURCHASE_ORDER_ITEMS : "contains items"
    PURCHASE_ORDERS ||--o{ FINANCIAL_TRANSACTIONS : "triggers payment"
    PURCHASE_ORDERS ||--o{ PURCHASES : "converted to purchase"

    IMPORT_BATCHES ||--o{ FINANCIAL_TRANSACTIONS : "imported finance rows"
    IMPORT_BATCHES ||--o{ PURCHASES : "imported purchase rows"
```

---

## 📖 Словарь данных (Data Dictionary)

### 1. `organizations` (Организации / Клиенты)
Корневая таблица мультитенантности. Представляет бизнес (кафе, кофейню, ресторан, торговую точку).

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | Уникальный ID организации |
| `name` | `VARCHAR(255)` | ❌ | — | Название заведения (напр., «Кофейня Арома», «Daily Cup») |
| `business_type` | `VARCHAR(100)` | ❌ | `'Кофейня'` | Тип бизнеса (Кофейня, Пекарня, Бар, Ресторан) |
| `currency` | `VARCHAR(20)` | ❌ | `'₸'` | Символ валюты учета (по умолчанию Казахстанский тенге `₸`) |
| `alert_threshold_percent` | `FLOAT` | ❌ | `5.0` | Порог отклонения цены (в %), при превышении которого создается алерт |
| `address` | `VARCHAR(255)` | ✔️ | `NULL` | Физический адрес заведения |
| `phone` | `VARCHAR(50)` | ✔️ | `NULL` | Контактный телефон |
| `email` | `VARCHAR(100)` | ✔️ | `NULL` | Официальный email организации |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время регистрации организации |

---

### 2. `users` (Пользователи и сотрудники)
Учетные записи сотрудников с ролевой моделью доступа (RBAC).

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | Уникальный ID пользователя |
| `organization_id` | `INTEGER` | ❌ FK | — | Ссылка на `organizations.id` (`ON DELETE CASCADE`) |
| `name` | `VARCHAR(255)` | ❌ | — | Полное имя сотрудника |
| `email` | `VARCHAR(255)` | ❌ UK | — | Уникальный email пользователя (индексирован) |
| `role` | `VARCHAR(50)` | ❌ | `'owner'` | Роль: `'owner'` (Владелец), `'manager'` (Управляющий), `'employee'` (Сотрудник) |
| `password_hash` | `VARCHAR(255)` | ✔️ | `NULL` | Хеш пароля (PBKDF2-HMAC-SHA256, 100 000 итераций) |
| `is_active` | `BOOLEAN` | ❌ | `TRUE` | Флаг активности аккаунта |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Дата и время создания |

---

### 3. `products` (Товары и ингредиенты)
Справочник номенклатуры склада (сырье, полуфабрикаты, упаковка, химия).

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | Идентификатор товара |
| `organization_id` | `INTEGER` | ❌ FK | — | Ссылка на `organizations.id` (`ON DELETE CASCADE`) |
| `name` | `VARCHAR(255)` | ❌ | — | Название позиции (индексировано) |
| `sku` | `VARCHAR(50)` | ✔️ | `NULL` | Артикул номенклатуры (индексирован) |
| `category` | `VARCHAR(100)` | ❌ | — | Категория (`Кофе`, `Молоко и сиропы`, `Упаковка`, `Выпечка`, `Чай`) |
| `unit` | `VARCHAR(50)` | ❌ | `'шт'` | Базовая единица списания (`кг`, `л`, `шт`, `пач`) |
| `unit_ratio` | `FLOAT` | ❌ | `1.0` | Коэффициент пересчета базовой единицы |
| `package_quantity` | `FLOAT` | ❌ | `1.0` | Объем в упаковке закупки |
| `package_unit` | `VARCHAR(50)` | ❌ | `'шт'` | Единица упаковки (`пакет 1кг`, `короб 12л`, `тубус`) |
| `current_stock` | `FLOAT` | ❌ | `0.0` | Текущий фактический остаток на складе |
| `minimum_stock` | `FLOAT` | ❌ | `0.0` | Неснижаемый страховой запас (триггер алертов низкого остатка) |
| `description` | `TEXT` | ✔️ | `NULL` | Подробное описание и требования к качеству |
| `is_active` | `BOOLEAN` | ❌ | `TRUE` | Флаг доступности номенклатуры |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Дата создания карточки товара |

---

### 4. `suppliers` (Поставщики)
Контрагенты, поставляющие сырье и расходные материалы.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | Уникальный ID поставщика |
| `organization_id` | `INTEGER` | ✔️ FK | `NULL` | Ссылка на `organizations.id` (`NULL` для глобальных поставщиков) |
| `name` | `VARCHAR(255)` | ❌ | — | Название компании (индексировано) |
| `contact_name` | `VARCHAR(255)` | ✔️ | `NULL` | ФИО менеджера поставщика |
| `phone` | `VARCHAR(50)` | ✔️ | `NULL` | Контактный номер телефона |
| `email` | `VARCHAR(100)` | ✔️ | `NULL` | Рабочий email контрагента |
| `address` | `VARCHAR(255)` | ✔️ | `NULL` | Адрес склада/офиса отгрузки |
| `notes` | `TEXT` | ✔️ | `NULL` | Дополнительные условия (график отгрузок, отсрочка) |
| `delivery_cost` | `FLOAT` | ❌ | `0.0` | Базовая стоимость доставки за заказ (₸) |
| `minimum_order_amount` | `FLOAT` | ❌ | `0.0` | Минимальная сумма заказа (MOA) для оформления (₸) |
| `source_type` | `VARCHAR(50)` | ❌ | `'imported'` | Источник: `'global'` (маркетплейс), `'imported'` (Excel/CSV), `'manual'` |
| `is_global` | `BOOLEAN` | ❌ | `FALSE` | Доступен ли поставщик всем арендаторам системы |
| `is_demo` | `BOOLEAN` | ❌ | `TRUE` | Флаг демонстрационных данных |
| `is_active` | `BOOLEAN` | ❌ | `TRUE` | Статус сотрудничества |

---

### 5. `supplier_offers` (Офферы поставщиков и прайс-лист)
Связка `Product ↔ Supplier` с актуальной ценой, минимальным квантом заказа (MOQ) и условиями.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | Уникальный ID ценового предложения |
| `organization_id` | `INTEGER` | ✔️ FK | `NULL` | Владелец оффера (`NULL` для глобального каталога) |
| `product_id` | `INTEGER` | ❌ FK | — | Товар (`products.id`, `ON DELETE CASCADE`) |
| `supplier_id` | `INTEGER` | ❌ FK | — | Поставщик (`suppliers.id`, `ON DELETE CASCADE`) |
| `offered_price` | `FLOAT` | ❌ | — | Цена за единицу продукции (₸) |
| `unit` | `VARCHAR(50)` | ❌ | — | Единица измерения предложения |
| `package_quantity` | `FLOAT` | ❌ | `1.0` | Количество в одной упаковке |
| `minimum_order_quantity` | `FLOAT` | ❌ | `1.0` | Минимальный объем заказа товара (MOQ в единицах) |
| `delivery_cost` | `FLOAT` | ❌ | `0.0` | Дополнительная стоимость логистики позиции |
| `valid_until` | `DATE` | ✔️ | `NULL` | Срок действия текущего прайса |
| `updated_at` | `DATETIME` | ❌ | `utcnow` | Время последней фиксации цены |
| `source_type` | `VARCHAR(50)` | ❌ | `'mock'` | Тип источника (`'mock'`, `'api'`, `'file'`) |
| `price_source` | `VARCHAR(50)` | ❌ | `'catalog'` | Источник цены: `'catalog'`, `'user_import'`, `'manual'` |
| `is_demo` | `BOOLEAN` | ❌ | `TRUE` | Флаг демо-прайса |
| `is_active` | `BOOLEAN` | ❌ | `TRUE` | Действует ли предложение |

---

### 6. `offer_price_history` (История изменения цен поставщиков)
Неизменяемый журнал (Audit Trail) динамики цен по офферам поставщиков.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID записи истории |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `offer_id` | `INTEGER` | ✔️ FK | `NULL` | Ссылка на `supplier_offers.id` (`ON DELETE SET NULL`) |
| `product_id` | `INTEGER` | ❌ FK | — | `products.id` (`ON DELETE CASCADE`) |
| `supplier_id` | `INTEGER` | ❌ FK | — | `suppliers.id` (`ON DELETE CASCADE`) |
| `old_price` | `FLOAT` | ❌ | — | Предыдущая цена за единицу (₸) |
| `new_price` | `FLOAT` | ❌ | — | Новая зафиксированная цена (₸) |
| `change_percent` | `FLOAT` | ❌ | `0.0` | Процент изменения: `((new - old) / old) * 100` |
| `changed_at` | `DATETIME` | ❌ | `utcnow` | Момент фиксации изменения цены |

---

### 7. `purchase_orders` (Заказы поставщикам)
Документы закупки сырья у поставщика.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID заказа |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `order_number` | `VARCHAR(50)` | ❌ | — | Номер документа (напр., `PO-2026-0042`, индексирован) |
| `supplier_id` | `INTEGER` | ❌ FK | — | Поставщик (`suppliers.id`, `ON DELETE RESTRICT`) |
| `order_date` | `DATE` | ❌ | — | Дата формирования заказа (индексирована) |
| `status` | `VARCHAR(20)` | ❌ | `'draft'` | Статус: `'draft'`, `'confirmed'`, `'received'`, `'cancelled'` |
| `subtotal_amount` | `FLOAT` | ❌ | `0.0` | Сумма позиций без учета доставки (₸) |
| `delivery_cost` | `FLOAT` | ❌ | `0.0` | Стоимость доставки данного поставщика (₸) |
| `total_amount` | `FLOAT` | ❌ | `0.0` | Итоговая сумма к оплате: `subtotal + delivery_cost` |
| `notes` | `TEXT` | ✔️ | `NULL` | Комментарии к заказу и доставке |
| `created_by_user_id`| `INTEGER` | ✔️ FK | `NULL` | Автор заказа (`users.id`, `ON DELETE SET NULL`) |
| `received_at` | `DATETIME` | ✔️ | `NULL` | Дата и время фактической приемки на склад |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время создания заказа |

---

### 8. `purchase_order_items` (Спецификация позиций заказа)
Строки документа заказа на поставку.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID строки заказа |
| `purchase_order_id`| `INTEGER` | ❌ FK | — | `purchase_orders.id` (`ON DELETE CASCADE`) |
| `product_id` | `INTEGER` | ❌ FK | — | Заказываемый товар (`products.id`, `ON DELETE RESTRICT`) |
| `ordered_quantity` | `FLOAT` | ❌ | — | Заказанное количество |
| `received_quantity`| `FLOAT` | ✔️ | `NULL` | Фактически принятое количество при оприходовании |
| `unit` | `VARCHAR(50)` | ❌ | — | Единица измерения позиции |
| `unit_price` | `FLOAT` | ❌ | — | Зафиксированная цена каталога на момент заказа (₸) |
| `total_price` | `FLOAT` | ❌ | — | Стоимость строки: `ordered_quantity * unit_price` |

---

### 9. `inventory_movements` (Партионный учет и складские движения)
Неизменяемый журнал всех перемещений остатков на складе.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID движения |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `product_id` | `INTEGER` | ❌ FK | — | `products.id` (`ON DELETE CASCADE`) |
| `movement_type` | `VARCHAR(30)` | ❌ | — | Тип: `'receipt'` (приход), `'write_off'` (списание), `'adjustment'` (инвентаризация), `'initial_stock'` |
| `quantity` | `FLOAT` | ❌ | — | Объем операции (положительное число) |
| `unit` | `VARCHAR(50)` | ❌ | — | Единица измерения |
| `previous_stock` | `FLOAT` | ❌ | `0.0` | Остаток на складе **до** проведения операции |
| `resulting_stock` | `FLOAT` | ❌ | `0.0` | Остаток на складе **после** проведения операции |
| `reason` | `VARCHAR(255)` | ❌ | — | Обоснование («Приемка по заказу PO-2026-001», «Порча», «Коррекция») |
| `reference_id` | `VARCHAR(100)` | ✔️ | `NULL` | Ссылка на документ-основание |
| `user_id` | `INTEGER` | ✔️ FK | `NULL` | Ответственный сотрудник (`users.id`, `ON DELETE SET NULL`) |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время проведения складской операции |

---

### 10. `purchases` (Архив фактов закупок)
Денормализованный журнал оприходованных закупок для аналитических отчетов и импортов.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID закупки |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `product_id` | `INTEGER` | ❌ FK | — | `products.id` (`ON DELETE CASCADE`) |
| `supplier_id` | `INTEGER` | ❌ FK | — | `suppliers.id` (`ON DELETE CASCADE`) |
| `purchase_date` | `DATE` | ❌ | — | Дата поставки (индексирована) |
| `quantity` | `FLOAT` | ❌ | — | Закупленный объем |
| `unit` | `VARCHAR(50)` | ❌ | — | Единица измерения |
| `unit_price` | `FLOAT` | ❌ | — | Цена за единицу (₸) |
| `total_price` | `FLOAT` | ❌ | — | Сумма закупки (₸) |
| `source` | `VARCHAR(50)` | ❌ | `'legacy_import'` | Источник (`'legacy_import'`, `'order_fulfillment'`, `'manual'`) |
| `import_batch_id` | `INTEGER` | ✔️ FK | `NULL` | Ссылка на пакет импорта (`ON DELETE SET NULL`) |
| `purchase_order_id`| `INTEGER` | ✔️ FK | `NULL` | Ссылка на заказ `purchase_orders.id` (`ON DELETE SET NULL`) |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время создания записи |

---

### 11. `financial_transactions` (ДДС и транзакции)
Журнал учета денежных потоков (доходы и расходы).

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID транзакции |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `transaction_date` | `DATE` | ❌ | — | Дата платежа (индексирована) |
| `description` | `VARCHAR(255)` | ❌ | — | Назначение платежа |
| `category` | `VARCHAR(100)` | ❌ | — | Категория расхода/дохода (`Сырье и закупки`, `Аренда`, `ФОТ`, `Выручка`) |
| `amount` | `FLOAT` | ❌ | — | Сумма транзакции (₸) |
| `transaction_type` | `VARCHAR(20)` | ❌ | `'expense'` | Тип: `'expense'` (расход) или `'income'` (доход) |
| `payment_method` | `VARCHAR(50)` | ❌ | `'cashless'`| Метод оплаты (`'cashless'`, `'cash'`, `'card'`) |
| `source` | `VARCHAR(50)` | ❌ | `'manual'` | Источник транзакции (`'manual'`, `'order_payment'`, `'import'`) |
| `supplier_id` | `INTEGER` | ✔️ FK | `NULL` | Поставщик-получатель (`suppliers.id`, `ON DELETE SET NULL`) |
| `purchase_order_id`| `INTEGER` | ✔️ FK | `NULL` | Заказ-основание (`purchase_orders.id`, `ON DELETE SET NULL`) |
| `import_batch_id` | `INTEGER` | ✔️ FK | `NULL` | Пакет импорта выписки (`import_batches.id`, `ON DELETE SET NULL`) |
| `is_archived` | `BOOLEAN` | ❌ | `FALSE` | Флаг архивации транзакции |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время фиксации проводки |

---

### 12. `notifications` (Умные алерты и рекомендации)
Система уведомлений управляющего о рисках и экономии.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID уведомления |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `title` | `VARCHAR(255)` | ❌ | — | Заголовок алерта |
| `description` | `TEXT` | ❌ | — | Подробное описание и рекомендация решения |
| `severity` | `VARCHAR(20)` | ❌ | `'info'` | Критичность: `'warning'`, `'info'`, `'danger'`, `'success'` |
| `notification_type`| `VARCHAR(50)` | ❌ | — | Тип: `'price_spike'`, `'alternative_offer'`, `'low_stock'`, `'expense_change'`, `'stale_price'`, `'purchase_pending'` |
| `related_product_id`| `INTEGER` | ✔️ FK | `NULL` | Связанный товар (`products.id`, `ON DELETE SET NULL`) |
| `is_read` | `BOOLEAN` | ❌ | `FALSE` | Статус прочтения пользователем |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время генерации события |

---

### 13. `import_batches` (Пакеты импорта файлов)
История и аудит загрузок внешних реестров (Excel, CSV).

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID пакета импорта |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `file_name` | `VARCHAR(255)` | ❌ | — | Исходное имя загруженного файла |
| `import_type` | `VARCHAR(50)` | ❌ | — | Тип реестра: `'finances'`, `'purchases'`, `'inventory'`, `'supplier_prices'` |
| `status` | `VARCHAR(20)` | ❌ | `'success'` | Статус обработки: `'success'`, `'partial'`, `'failed'` |
| `rows_total` | `INTEGER` | ❌ | `0` | Общее количество обнаруженных строк |
| `rows_imported` | `INTEGER` | ❌ | `0` | Успешно обработано и добавлено записей |
| `rows_skipped` | `INTEGER` | ❌ | `0` | Пропущено строк (дубликаты, ошибки валидации) |
| `error_summary` | `TEXT` | ✔️ | `NULL` | Сводка предупреждений и ошибок валидации |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Дата и время загрузки |

---

### 14. `activity_logs` (Журнал аудита действий)
Неизменяемый журнал действий пользователей в соответствии с требованиями безопасности.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID лога |
| `organization_id` | `INTEGER` | ❌ FK | — | `organizations.id` (`ON DELETE CASCADE`) |
| `user_id` | `INTEGER` | ✔️ FK | `NULL` | Пользователь (`users.id`, `ON DELETE SET NULL`) |
| `user_name` | `VARCHAR(255)` | ✔️ | `NULL` | Имя пользователя на момент совершения операции |
| `action` | `VARCHAR(100)` | ❌ | — | Действие (`CREATE`, `UPDATE`, `DELETE`, `RECEIVE_ORDER`, `IMPORT`, `LOGIN`) |
| `entity_type` | `VARCHAR(100)` | ❌ | — | Тип сущности (`User`, `Product`, `PurchaseOrder`, `Supplier`, `ReportTemplate`) |
| `entity_id` | `VARCHAR(100)` | ✔️ | `NULL` | Идентификатор затронутой сущности |
| `details` | `TEXT` | ✔️ | `NULL` | Детали операции (измененные поля, параметры) |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Точное время события |

---

### 15. `report_templates` (Шаблоны конструктора отчетов)
Хранилище пресетов и пользовательских отчетов с конфигурацией в формате JSON.

| Колонка | Тип | Nullable | Default | Описание |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ❌ PK | auto | ID шаблона |
| `organization_id` | `INTEGER` | ✔️ FK | `NULL` | `organizations.id` (`NULL` для системных шаблонов) |
| `title` | `VARCHAR(255)` | ❌ | — | Название отчета |
| `description` | `TEXT` | ✔️ | `NULL` | Описание назначения отчета |
| `report_type` | `VARCHAR(50)` | ❌ | — | Тип отчета: `'financial'`, `'procurement'`, `'inventory'`, `'executive'` |
| `config` | `TEXT` | ❌ | — | JSON-конфигурация секций, группировки, фильтров и сортировки |
| `is_system` | `BOOLEAN` | ❌ | `FALSE` | Является ли шаблон системным пресетом |
| `is_archived` | `BOOLEAN` | ❌ | `FALSE` | Помещен ли шаблон в архив |
| `created_by_user_id`| `INTEGER` | ✔️ FK | `NULL` | Автор шаблона (`users.id`, `ON DELETE SET NULL`) |
| `created_at` | `DATETIME` | ❌ | `utcnow` | Время создания |
| `updated_at` | `DATETIME` | ❌ | `utcnow` | Время последнего редактирования конфигурации |

---

## 🔄 Жизненные циклы и бизнес-логика

### 1. Жизненный цикл заказа на закупку (Purchase Order State Machine)

```mermaid
stateDiagram-v2
    [*] --> draft : Создание заказа с позициями из каталога поставщика
    draft --> draft : Редактирование (изменение количеств, добавление/удаление позиций)
    draft --> cancelled : Отмена черновика
    draft --> confirmed : Подтверждение и отправка поставщику
    confirmed --> cancelled : Отмена до отгрузки
    confirmed --> received : Оприходование на складе
    received --> [*] : Склад пополнен, расход зафиксирован
    cancelled --> [*] : Заказ закрыт без складских проводок
```

* **При создании/редактировании черновика (`draft`)**:
  * Цены жестко блокируются по актуальному каталогу выбранного поставщика (`supplier_offers.offered_price`).
  * Валидируется кратность и минимальный объем закупки (`ordered_quantity >= minimum_order_quantity`).
  * Валидируется минимальная сумма поставки поставщика (`subtotal_amount >= minimum_order_amount`).
* **При оприходовании (`received`)**:
  1. Статус меняется на `received`, фиксируется `received_at = utcnow()`.
  2. Для каждой позиции создается запись `InventoryMovement` с типом `receipt`, `previous_stock`, `resulting_stock = previous_stock + received_quantity`.
  3. В таблице `products` увеличивается `current_stock += received_quantity`.
  4. Автоматически создается проводка `FinancialTransaction` (тип `expense`, сумма `total_amount`, категория `Сырье и материалы`).
  5. Создается запись `Purchase` для быстрой аналитики и исторического следа.
  6. В `ActivityLog` пишется аудит-запись `RECEIVE_ORDER`.

---

## 🛠️ Миграции и авто-эволюция схемы

В модуле [`backend/src/backend/migrations.py`](file:///home/disortus/coop-projs/BizMind/backend/src/backend/migrations.py) реализован встроенный механизм автоматических миграций:

1. При запуске сервиса вызывается `run_auto_migrations()`.
2. Функция инспектирует все таблицы и колонки СУБД с помощью `sqlalchemy.inspect(engine)`.
3. При обнаружении новых полей, добавленных в модели SQLAlchemy, автоматически генерируются и исполняются команды:
   ```sql
   ALTER TABLE <table_name> ADD COLUMN <col_name> <TYPE> [DEFAULT <val>];
   ```
4. Выполняется бэкфилл дефолтных значений для существующих строк с `NULL`.
5. Это обеспечивает плавные обновления без потери пользовательских данных и без необходимости ручных миграций при локальном и контейнерном запуске.

---

## 🌱 Демо-данные и сидирование

База данных поддерживает детерминированное сидирование через API (`POST /api/demo/reset`) и CLI-скрипт [`backend/src/backend/demo/seed_data.py`](file:///home/disortus/coop-projs/BizMind/backend/src/backend/demo/seed_data.py).

### Структура предзаполненных сценариев:

1. **Глобальный маркетплейс поставщиков (`is_global = True`)**:
   * 8 реальных поставщиков г. Астана и Казахстана (ТОО "Coffee Trade KZ", "MasterBarista Distribution", ТОО "PackService Astana", ТОО "Астана-Сладкоежка", "EcoDisposables KZ", ТОО "SilkWay Coffee Roasters", "Qazaq Dairy", "CleanPro Kazakhstan").
   * Более 40 актуальных офферов с ценами, MOQ и стоимостью доставки.
2. **Системные шаблоны отчетов (4 пресета)**:
   * Ежемесячный финансовый отчёт
   * Анализ закупок и динамики цен
   * Складской аудит и неснижаемые остатки
   * Экспресс-отчёт руководителя (Executive Summary)
3. **Сценарий А: «Кофейня Арома» (`id = 1`)**:
   * Чистое состояние нового заведения.
   * Базовые карточки 8 ключевых продуктов.
   * 0 транзакций, 0 закупок. Идеально для демонстрации первого импорта Excel/CSV и создания первого заказа.
4. **Сценарий Б: «Daily Cup» (`id = 2`)**:
   * Зрелый бизнес с 6-месячной операционной историей (апрель — октябрь 2026).
   * 120 финансовых транзакций, 72 фактические поставки.
   * Рассчитанная подтвержденная экономия 450 000+ ₸.
   * Алерты скачков цен и предсказания скорого исчерпания склада.

---

## 📈 Аналитические запросы и алгоритмы

### 1. Детекция скачков цен (Price Spike Alert)
```sql
SELECT 
    p.name AS product_name,
    s.name AS supplier_name,
    h.old_price,
    h.new_price,
    h.change_percent,
    h.changed_at
FROM offer_price_history h
JOIN products p ON p.id = h.product_id
JOIN suppliers s ON s.id = h.supplier_id
WHERE h.organization_id = :org_id 
  AND h.change_percent >= :threshold_percent
ORDER BY h.changed_at DESC;
```

### 2. Прогноз исчерпания склада (Inventory Burn Rate & Depletion)
* **Среднедневной расход** ($BurnRate$):
  $$BurnRate = \frac{\sum \text{quantity (movements: write\_off)}}{\text{days in window (e.g. 14 days)}}$$
* **Дней до исчерпания** ($DaysRemaining$):
  $$DaysRemaining = \frac{\text{Product.current\_stock}}{BurnRate}$$
* **Условие алерта**: если $DaysRemaining \le 3$ или $Product.current\_stock \le Product.minimum\_stock$.

### 3. Расчет фактической экономии (Realized Savings)
$$\text{Savings} = \sum (\text{BaselineMarketPrice}_i - \text{ActualPurchasedPrice}_i) \times \text{Quantity}_i$$

---

## 💾 Персистентность и обслуживание в Docker

### Конфигурация хранения данных

В `docker-compose.yml` настроен именованный volume:
```yaml
services:
  backend:
    volumes:
      - bizmind_db_data:/app

volumes:
  bizmind_db_data:
```
Файл базы данных `bizmind.db` сохраняется внутри Docker volume и не теряется при перезапусках контейнеров `docker compose down && docker compose up -d`.

### Резервное копирование (Backup)
Для создания горячей резервной копии SQLite без остановки сервиса:
```bash
# Внутри контейнера или локально:
sqlite3 bizmind.db ".backup 'bizmind_backup_$(date +%Y%m%d_%H%M%S).db'"
```

### Проверка целостности (Integrity Check)
```bash
sqlite3 bizmind.db "PRAGMA integrity_check;"
# Ожидаемый результат: ok
```
