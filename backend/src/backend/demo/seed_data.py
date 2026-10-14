from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models.models import (
    Organization,
    User,
    Product,
    Supplier,
    Purchase,
    SupplierOffer,
    FinancialTransaction,
    Notification,
    ImportBatch,
)

def reset_and_seed_db(db: Session) -> dict:
    # Drop and recreate all tables for a clean, deterministic state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    today = date(2026, 10, 14)

    # 1. Organization
    org = Organization(
        id=1,
        name="Кофейня «Cafe Aroma»",
        business_type="Кофейня / Общепит",
        created_at=datetime(2026, 5, 1, 9, 0, 0),
    )
    db.add(org)
    db.flush()

    # 2. User
    user = User(
        id=1,
        organization_id=org.id,
        name="Алексей Смирнов",
        email="demo@bizmind.kz",
        role="Управляющий / Владелец",
        created_at=datetime(2026, 5, 1, 9, 30, 0),
    )
    db.add(user)
    db.flush()

    # 3. Suppliers
    suppliers_data = [
        {
            "id": 1,
            "name": "Coffee Roasters Hub",
            "contact_name": "Иван Рустемов (+7 701 555-01-23)",
            "delivery_cost": 2500.0,
            "minimum_order_amount": 30000.0,
            "source_type": "manual",
            "is_demo": True,
        },
        {
            "id": 2,
            "name": "Aroma Direct",
            "contact_name": "Марат Омаров (+7 705 444-12-89)",
            "delivery_cost": 0.0,
            "minimum_order_amount": 25000.0,
            "source_type": "mock_catalog",
            "is_demo": True,
        },
        {
            "id": 3,
            "name": "BeanTrade Almaty",
            "contact_name": "Отдел оптовых продаж (+7 727 312-88-99)",
            "delivery_cost": 1500.0,
            "minimum_order_amount": 40000.0,
            "source_type": "mock_catalog",
            "is_demo": True,
        },
        {
            "id": 4,
            "name": "Premium Coffee Express",
            "contact_name": "Служба поставок (+7 700 888-21-34)",
            "delivery_cost": 0.0,
            "minimum_order_amount": 10000.0,
            "source_type": "mock_catalog",
            "is_demo": True,
        },
        {
            "id": 5,
            "name": "Almaty Dairy Group",
            "contact_name": "Складской отдел (+7 702 111-90-44)",
            "delivery_cost": 1000.0,
            "minimum_order_amount": 15000.0,
            "source_type": "manual",
            "is_demo": True,
        },
        {
            "id": 6,
            "name": "Qazaq Milk Line",
            "contact_name": "Менеджер Асель (+7 707 988-77-66)",
            "delivery_cost": 0.0,
            "minimum_order_amount": 20000.0,
            "source_type": "mock_catalog",
            "is_demo": True,
        },
        {
            "id": 7,
            "name": "Barista Pro Supplies",
            "contact_name": "Владимир Ким (+7 700 333-22-11)",
            "delivery_cost": 1200.0,
            "minimum_order_amount": 10000.0,
            "source_type": "manual",
            "is_demo": True,
        },
        {
            "id": 8,
            "name": "SweetSyrup Co",
            "contact_name": "Татьяна Белова (+7 701 444-55-66)",
            "delivery_cost": 0.0,
            "minimum_order_amount": 15000.0,
            "source_type": "mock_catalog",
            "is_demo": True,
        },
        {
            "id": 9,
            "name": "EcoPack Kazakhstan",
            "contact_name": "Динара Сатпаева (+7 777 654-32-10)",
            "delivery_cost": 1800.0,
            "minimum_order_amount": 20000.0,
            "source_type": "manual",
            "is_demo": True,
        },
        {
            "id": 10,
            "name": "Global Pack Almaty",
            "contact_name": "Оптовый отдел (+7 708 222-44-55)",
            "delivery_cost": 1000.0,
            "minimum_order_amount": 25000.0,
            "source_type": "mock_catalog",
            "is_demo": True,
        },
    ]
    for s in suppliers_data:
        sup = Supplier(
            id=s["id"],
            organization_id=org.id,
            name=s["name"],
            contact_name=s["contact_name"],
            delivery_cost=s["delivery_cost"],
            minimum_order_amount=s["minimum_order_amount"],
            source_type=s["source_type"],
            is_demo=s["is_demo"],
        )
        db.add(sup)
    db.flush()

    # 4. Products
    products_data = [
        {
            "id": 1,
            "name": "Кофе в зернах Espresso Blend 100% Арабика",
            "category": "Кофе",
            "unit": "кг",
            "package_quantity": 1.0,
            "package_unit": "кг",
            "current_stock": 18.0,
            "minimum_stock": 15.0,
        },
        {
            "id": 2,
            "name": "Молоко ультрапастеризованное 3.2%",
            "category": "Молочная продукция",
            "unit": "л",
            "package_quantity": 1.0,
            "package_unit": "л",
            "current_stock": 12.0,  # Critical low stock!
            "minimum_stock": 25.0,
        },
        {
            "id": 3,
            "name": "Сироп Ваниль 1л",
            "category": "Сиропы и топпинги",
            "unit": "бут",
            "package_quantity": 1.0,
            "package_unit": "бут",
            "current_stock": 4.0,  # Low stock!
            "minimum_stock": 5.0,
        },
        {
            "id": 4,
            "name": "Сироп Карамель 1л",
            "category": "Сиропы и топпинги",
            "unit": "бут",
            "package_quantity": 1.0,
            "package_unit": "бут",
            "current_stock": 7.0,
            "minimum_stock": 5.0,
        },
        {
            "id": 5,
            "name": "Стаканы бумажные двухслойные 350мл (50 шт)",
            "category": "Упаковка и расходники",
            "unit": "упак",
            "package_quantity": 50.0,
            "package_unit": "шт",
            "current_stock": 14.0,
            "minimum_stock": 10.0,
        },
        {
            "id": 6,
            "name": "Крышки для стаканов 80мм (100 шт)",
            "category": "Упаковка и расходники",
            "unit": "упак",
            "package_quantity": 100.0,
            "package_unit": "шт",
            "current_stock": 8.0,  # Low stock!
            "minimum_stock": 10.0,
        },
        {
            "id": 7,
            "name": "Салфетки барные 24x24 (400 шт)",
            "category": "Упаковка и расходники",
            "unit": "упак",
            "package_quantity": 400.0,
            "package_unit": "шт",
            "current_stock": 12.0,
            "minimum_stock": 8.0,
        },
        {
            "id": 8,
            "name": "Трубочки биоразлагаемые (200 шт)",
            "category": "Упаковка и расходники",
            "unit": "упак",
            "package_quantity": 200.0,
            "package_unit": "шт",
            "current_stock": 9.0,
            "minimum_stock": 5.0,
        },
        {
            "id": 9,
            "name": "Чай листовой черный Ассам",
            "category": "Чай",
            "unit": "кг",
            "package_quantity": 1.0,
            "package_unit": "кг",
            "current_stock": 3.5,
            "minimum_stock": 2.0,
        },
        {
            "id": 10,
            "name": "Чай зеленый Сенча",
            "category": "Чай",
            "unit": "кг",
            "package_quantity": 1.0,
            "package_unit": "кг",
            "current_stock": 2.5,
            "minimum_stock": 2.0,
        },
    ]
    for p in products_data:
        prod = Product(
            id=p["id"],
            organization_id=org.id,
            name=p["name"],
            category=p["category"],
            unit=p["unit"],
            package_quantity=p["package_quantity"],
            package_unit=p["package_unit"],
            current_stock=p["current_stock"],
            minimum_stock=p["minimum_stock"],
            created_at=datetime(2026, 6, 1, 10, 0, 0),
        )
        db.add(prod)
    db.flush()

    # 5. Legacy Import Batches records
    batch_finances = ImportBatch(
        id=1,
        organization_id=org.id,
        file_name="legacy_finances.xlsx",
        import_type="finances",
        status="success",
        rows_total=48,
        rows_imported=48,
        rows_skipped=0,
        error_summary="Успешно импортированы исторические транзакции кофейни за 4 месяца",
        created_at=datetime(2026, 10, 10, 14, 20, 0),
    )
    batch_purchases = ImportBatch(
        id=2,
        organization_id=org.id,
        file_name="legacy_purchases.xlsx",
        import_type="purchases",
        status="success",
        rows_total=24,
        rows_imported=24,
        rows_skipped=0,
        error_summary="Успешно импортирована история закупок сырья и расходников",
        created_at=datetime(2026, 10, 10, 14, 22, 0),
    )
    db.add(batch_finances)
    db.add(batch_purchases)
    db.flush()

    # 6. Purchases
    # Coffee Purchases: 3 past at 10,000 and 1 latest at 11,500 (+15%)
    purchases_records = [
        # Coffee
        (1, 1, today - timedelta(days=85), 25.0, "кг", 10000.0, 250000.0),
        (1, 1, today - timedelta(days=55), 25.0, "кг", 10000.0, 250000.0),
        (1, 1, today - timedelta(days=28), 25.0, "кг", 10000.0, 250000.0),
        (1, 1, today - timedelta(days=6), 25.0, "кг", 11500.0, 287500.0),  # Recent Spike!
        # Milk from Almaty Dairy Group (id 5)
        (2, 5, today - timedelta(days=95), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=80), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=65), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=50), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=35), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=20), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=5), 120.0, "л", 480.0, 57600.0),
        # Syrups from Barista Pro (id 7)
        (3, 7, today - timedelta(days=75), 6.0, "бут", 3900.0, 23400.0),
        (4, 7, today - timedelta(days=75), 6.0, "бут", 3900.0, 23400.0),
        (3, 7, today - timedelta(days=40), 6.0, "бут", 3900.0, 23400.0),
        (4, 7, today - timedelta(days=40), 6.0, "бут", 3900.0, 23400.0),
        (3, 7, today - timedelta(days=12), 6.0, "бут", 3900.0, 23400.0),
        (4, 7, today - timedelta(days=12), 6.0, "бут", 3900.0, 23400.0),
        # Packaging from EcoPack Kazakhstan (id 9)
        (5, 9, today - timedelta(days=90), 30.0, "упак", 1450.0, 43500.0),
        (6, 9, today - timedelta(days=90), 15.0, "упак", 980.0, 14700.0),
        (7, 9, today - timedelta(days=90), 20.0, "упак", 750.0, 15000.0),
        (5, 9, today - timedelta(days=60), 30.0, "упак", 1450.0, 43500.0),
        (6, 9, today - timedelta(days=60), 15.0, "упак", 980.0, 14700.0),
        (7, 9, today - timedelta(days=60), 20.0, "упак", 750.0, 15000.0),
        (5, 9, today - timedelta(days=30), 30.0, "упак", 1450.0, 43500.0),
        (6, 9, today - timedelta(days=30), 15.0, "упак", 980.0, 14700.0),
        (7, 9, today - timedelta(days=30), 20.0, "упак", 750.0, 15000.0),
        (5, 9, today - timedelta(days=8), 30.0, "упак", 1450.0, 43500.0),
        (6, 9, today - timedelta(days=8), 15.0, "упак", 980.0, 14700.0),
        (7, 9, today - timedelta(days=8), 20.0, "упак", 750.0, 15000.0),
        # Tea
        (9, 7, today - timedelta(days=75), 4.0, "кг", 5200.0, 20800.0),
        (9, 7, today - timedelta(days=20), 4.0, "кг", 5200.0, 20800.0),
    ]

    for p_id, s_id, p_date, qty, unit, u_price, tot_price in purchases_records:
        purch = Purchase(
            organization_id=org.id,
            product_id=p_id,
            supplier_id=s_id,
            purchase_date=p_date,
            quantity=qty,
            unit=unit,
            unit_price=u_price,
            total_price=tot_price,
            source="legacy_import",
            import_batch_id=batch_purchases.id,
            created_at=datetime.combine(p_date, datetime.min.time()),
        )
        db.add(purch)
    db.flush()

    # 7. Supplier Offers (Alternative prices)
    offers_data = [
        # Coffee offers:
        {
            "product_id": 1,
            "supplier_id": 2,  # Aroma Direct
            "offered_price": 10350.0,  # 11,500 - 10,350 = 1,150 KZT difference!
            "unit": "кг",
            "package_quantity": 1.0,
            "minimum_order_quantity": 20.0,
            "delivery_cost": 0.0,
            "updated_at": datetime(2026, 10, 12, 11, 0, 0),
        },
        {
            "product_id": 1,
            "supplier_id": 3,  # BeanTrade Almaty
            "offered_price": 10800.0,
            "unit": "кг",
            "package_quantity": 1.0,
            "minimum_order_quantity": 15.0,
            "delivery_cost": 1500.0,
            "updated_at": datetime(2026, 10, 10, 9, 30, 0),
        },
        {
            "product_id": 1,
            "supplier_id": 1,  # Coffee Roasters Hub (Current, high)
            "offered_price": 11500.0,
            "unit": "кг",
            "package_quantity": 1.0,
            "minimum_order_quantity": 10.0,
            "delivery_cost": 2500.0,
            "updated_at": datetime(2026, 10, 8, 16, 0, 0),
        },
        {
            "product_id": 1,
            "supplier_id": 4,  # Premium Coffee Express (Expensive)
            "offered_price": 12200.0,
            "unit": "кг",
            "package_quantity": 1.0,
            "minimum_order_quantity": 5.0,
            "delivery_cost": 0.0,
            "updated_at": datetime(2026, 10, 13, 10, 0, 0),
        },
        # Milk offers:
        {
            "product_id": 2,
            "supplier_id": 6,  # Qazaq Milk Line
            "offered_price": 440.0,  # 480 - 440 = 40 KZT savings/l
            "unit": "л",
            "package_quantity": 1.0,
            "minimum_order_quantity": 50.0,
            "delivery_cost": 0.0,
            "updated_at": datetime(2026, 10, 11, 14, 0, 0),
        },
        {
            "product_id": 2,
            "supplier_id": 5,  # Almaty Dairy Group (Current)
            "offered_price": 480.0,
            "unit": "л",
            "package_quantity": 1.0,
            "minimum_order_quantity": 40.0,
            "delivery_cost": 1000.0,
            "updated_at": datetime(2026, 10, 9, 12, 0, 0),
        },
        # Packaging:
        {
            "product_id": 5,
            "supplier_id": 10,  # Global Pack Almaty
            "offered_price": 1350.0,  # 1450 - 1350 = 100 KZT savings
            "unit": "упак",
            "package_quantity": 1.0,
            "minimum_order_quantity": 20.0,
            "delivery_cost": 1000.0,
            "updated_at": datetime(2026, 10, 9, 15, 0, 0),
        },
        {
            "product_id": 5,
            "supplier_id": 9,  # EcoPack Kazakhstan (Current)
            "offered_price": 1450.0,
            "unit": "упак",
            "package_quantity": 1.0,
            "minimum_order_quantity": 10.0,
            "delivery_cost": 1800.0,
            "updated_at": datetime(2026, 10, 7, 10, 0, 0),
        },
        # Syrups:
        {
            "product_id": 3,
            "supplier_id": 8,  # SweetSyrup Co
            "offered_price": 3650.0,  # 3900 - 3650 = 250 KZT savings
            "unit": "бут",
            "package_quantity": 1.0,
            "minimum_order_quantity": 4.0,
            "delivery_cost": 0.0,
            "updated_at": datetime(2026, 10, 10, 10, 0, 0),
        },
        {
            "product_id": 3,
            "supplier_id": 7,  # Barista Pro Supplies
            "offered_price": 3900.0,
            "unit": "бут",
            "package_quantity": 1.0,
            "minimum_order_quantity": 4.0,
            "delivery_cost": 1200.0,
            "updated_at": datetime(2026, 10, 6, 11, 0, 0),
        },
    ]

    for o in offers_data:
        offer = SupplierOffer(
            organization_id=org.id,
            product_id=o["product_id"],
            supplier_id=o["supplier_id"],
            offered_price=o["offered_price"],
            unit=o["unit"],
            package_quantity=o["package_quantity"],
            minimum_order_quantity=o["minimum_order_quantity"],
            delivery_cost=o["delivery_cost"],
            updated_at=o["updated_at"],
            source_type="mock",
            is_demo=True,
        )
        db.add(offer)
    db.flush()

    # 8. Financial Transactions (coincides with legacy_finances)
    fin_transactions = []
    # Fixed monthly costs for July, August, September, October 2026
    for offset_months, base_date in [
        (3, date(2026, 7, 1)),
        (2, date(2026, 8, 1)),
        (1, date(2026, 9, 1)),
        (0, date(2026, 10, 1)),
    ]:
        # Rent
        fin_transactions.append((base_date.replace(day=5), "Аренда помещения кофейни (ул. Абая 45)", "Аренда помещения", 650000.0, "expense"))
        # FOT
        fin_transactions.append((base_date.replace(day=10), "Аванс заработной платы бариста и смене", "Фонд оплаты труда", 425000.0, "expense"))
        fin_transactions.append((base_date.replace(day=25), "Окончательный расчет по ЗП", "Фонд оплаты труда", 425000.0, "expense"))
        # Utilities
        fin_transactions.append((base_date.replace(day=15), "Коммунальные услуги и электроэнергия", "Коммунальные услуги", 92000.0 + offset_months * 1800, "expense"))
        # Equipment service
        fin_transactions.append((base_date.replace(day=18), "ТО и чистка эспрессо-машины Nuova Simonelli", "Обслуживание оборудования", 45000.0, "expense"))

    # Purchases mirrored into finances:
    # 3 past coffee purchases at 250,000
    fin_transactions.append((today - timedelta(days=85), "Закупка кофе в зернах Espresso Blend (25 кг)", "Закупка кофе", 250000.0, "expense"))
    fin_transactions.append((today - timedelta(days=55), "Закупка кофе в зернах Espresso Blend (25 кг)", "Закупка кофе", 250000.0, "expense"))
    fin_transactions.append((today - timedelta(days=28), "Закупка кофе в зернах Espresso Blend (25 кг)", "Закупка кофе", 250000.0, "expense"))
    # Latest coffee purchase with price jump to 287,500
    fin_transactions.append((today - timedelta(days=6), "Закупка кофе в зернах Espresso Blend (25 кг по новой цене)", "Закупка кофе", 287500.0, "expense"))

    # Milk
    for days_ago in [95, 80, 65, 50, 35, 20, 5]:
        fin_transactions.append((today - timedelta(days=days_ago), "Закупка ультрапастеризованного молока 3.2% (120 л)", "Закупка молока и продуктов", 57600.0, "expense"))

    # Packaging
    for days_ago in [90, 60, 30, 8]:
        fin_transactions.append((today - timedelta(days=days_ago), "Заказ стаканов 350мл, крышек и барных салфеток", "Расходные материалы", 78500.0, "expense"))

    # Syrups & tea
    for days_ago in [75, 40, 12]:
        fin_transactions.append((today - timedelta(days=days_ago), "Пополнение запаса сиропов (Ваниль, Карамель) и листового чая", "Закупка молока и продуктов", 42000.0, "expense"))

    # Incomes (Weekly Revenues)
    for i in range(15):
        dt = today - timedelta(days=i * 7 + 2)
        fin_transactions.append((dt, "Выручка кофейни за неделю (касса + безналичный эквайринг)", "Выручка / Продажи", 710000.0 + (i % 3) * 35000, "income"))

    for t_date, desc, cat, amt, t_type in fin_transactions:
        tx = FinancialTransaction(
            organization_id=org.id,
            transaction_date=t_date,
            description=desc,
            category=cat,
            amount=amt,
            transaction_type=t_type,
            source="legacy_import",
            import_batch_id=batch_finances.id,
            created_at=datetime.combine(t_date, datetime.min.time()),
        )
        db.add(tx)
    db.flush()

    # 9. Dynamic Notifications based on data
    notifications_data = [
        {
            "title": "Повышение цены на кофе +15.0%",
            "description": "Поставщик Coffee Roasters Hub повысил цену на «Кофе в зернах Espresso Blend 100% Арабика» с 10 000 ₸ до 11 500 ₸/кг (+1 500 ₸ за ед.).",
            "severity": "danger",
            "notification_type": "price_spike",
            "related_product_id": 1,
            "created_at": datetime.combine(today - timedelta(days=6), datetime.min.time()) + timedelta(hours=14),
        },
        {
            "title": "Обнаружено альтернативное предложение по кофе",
            "description": "Поставщик Aroma Direct предлагает сопоставимый товар за 10 350 ₸/кг. Потенциальная разница — 1 150 ₸/кг (до 23 000 ₸ на партию 20 кг).",
            "severity": "success",
            "notification_type": "alternative_offer",
            "related_product_id": 1,
            "created_at": datetime.combine(today - timedelta(days=2), datetime.min.time()) + timedelta(hours=11),
        },
        {
            "title": "Критический остаток: молоко 3.2%",
            "description": "Текущий остаток молока составляет 12 л при минимальном пороге 25 л. При среднем потреблении 8 л/день запаса хватит на 1.5 дня.",
            "severity": "warning",
            "notification_type": "low_stock",
            "related_product_id": 2,
            "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()) + timedelta(hours=9),
        },
        {
            "title": "Заканчиваются крышки для стаканов 80мм",
            "description": "Остаток «Крышки для стаканов 80мм» — 8 упак при минимальном запасе 10 упак. Рекомендуется включить в ближайший заказ.",
            "severity": "warning",
            "notification_type": "low_stock",
            "related_product_id": 6,
            "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()) + timedelta(hours=16),
        },
        {
            "title": "Рост расходов в категории «Закупка кофе»",
            "description": "Расходы на кофе в октябре выросли на 15.0% из-за изменения базового тарифа поставщика.",
            "severity": "info",
            "notification_type": "expense_change",
            "related_product_id": 1,
            "created_at": datetime.combine(today, datetime.min.time()) + timedelta(hours=8),
        },
    ]

    for n in notifications_data:
        notif = Notification(
            organization_id=org.id,
            title=n["title"],
            description=n["description"],
            severity=n["severity"],
            notification_type=n["notification_type"],
            related_product_id=n["related_product_id"],
            is_read=False,
            created_at=n["created_at"],
        )
        db.add(notif)

    db.commit()

    return {
        "status": "success",
        "message": "Демо-база Cafe Aroma успешно инициализирована",
        "organization": org.name,
        "products_count": len(products_data),
        "suppliers_count": len(suppliers_data),
        "purchases_count": len(purchases_records),
        "transactions_count": len(fin_transactions),
        "offers_count": len(offers_data),
        "notifications_count": len(notifications_data),
    }

if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = reset_and_seed_db(db)
        print("Seed result:", res)
    finally:
        db.close()
