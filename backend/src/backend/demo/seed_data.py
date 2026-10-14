from datetime import date, datetime, timedelta
from typing import Dict, Any
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


def reset_and_seed_db(db: Session) -> Dict[str, Any]:
    # Drop and recreate all tables for a clean, deterministic state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    today = date(2026, 10, 14)

    # =========================================================================
    # ORGANIZATION 1: CAFE AROMA (Initial Migration Scenario)
    # =========================================================================
    org1 = Organization(
        id=1,
        name="Кофейня «Cafe Aroma»",
        business_type="Кофейня / Общепит",
        created_at=datetime(2026, 5, 1, 9, 0, 0),
    )
    db.add(org1)
    db.flush()

    user1 = User(
        id=1,
        organization_id=org1.id,
        name="Алексей Смирнов",
        email="demo@bizmind.kz",
        role="Управляющий / Владелец",
        created_at=datetime(2026, 5, 1, 9, 30, 0),
    )
    db.add(user1)
    db.flush()

    # Suppliers for Org 1
    suppliers1_data = [
        {"id": 1, "name": "Coffee Roasters Hub", "contact_name": "Иван Рустемов (+7 701 555-01-23)", "delivery_cost": 2500.0, "minimum_order_amount": 30000.0, "source_type": "manual", "is_demo": True},
        {"id": 2, "name": "Aroma Direct", "contact_name": "Марат Омаров (+7 705 444-12-89)", "delivery_cost": 0.0, "minimum_order_amount": 25000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 3, "name": "BeanTrade Almaty", "contact_name": "Отдел оптовых продаж (+7 727 312-88-99)", "delivery_cost": 1500.0, "minimum_order_amount": 40000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 4, "name": "Premium Coffee Express", "contact_name": "Служба поставок (+7 700 888-21-34)", "delivery_cost": 0.0, "minimum_order_amount": 10000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 5, "name": "Almaty Dairy Group", "contact_name": "Складской отдел (+7 702 111-90-44)", "delivery_cost": 1000.0, "minimum_order_amount": 15000.0, "source_type": "manual", "is_demo": True},
        {"id": 6, "name": "Qazaq Milk Line", "contact_name": "Менеджер Асель (+7 707 988-77-66)", "delivery_cost": 0.0, "minimum_order_amount": 20000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 7, "name": "Barista Pro Supplies", "contact_name": "Владимир Ким (+7 700 333-22-11)", "delivery_cost": 1200.0, "minimum_order_amount": 10000.0, "source_type": "manual", "is_demo": True},
        {"id": 8, "name": "SweetSyrup Co", "contact_name": "Татьяна Белова (+7 701 444-55-66)", "delivery_cost": 0.0, "minimum_order_amount": 15000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 9, "name": "EcoPack Kazakhstan", "contact_name": "Динара Сатпаева (+7 777 654-32-10)", "delivery_cost": 1800.0, "minimum_order_amount": 20000.0, "source_type": "manual", "is_demo": True},
        {"id": 10, "name": "Global Pack Almaty", "contact_name": "Оптовый отдел (+7 708 222-44-55)", "delivery_cost": 1000.0, "minimum_order_amount": 25000.0, "source_type": "mock_catalog", "is_demo": True},
    ]
    for s in suppliers1_data:
        db.add(Supplier(
            id=s["id"], organization_id=org1.id, name=s["name"], contact_name=s["contact_name"],
            delivery_cost=s["delivery_cost"], minimum_order_amount=s["minimum_order_amount"],
            source_type=s["source_type"], is_demo=s["is_demo"]
        ))
    db.flush()

    # Products for Org 1
    products1_data = [
        {"id": 1, "name": "Кофе в зернах Espresso Blend 100% Арабика", "category": "Кофе", "unit": "кг", "package_quantity": 1.0, "package_unit": "кг", "current_stock": 18.0, "minimum_stock": 15.0},
        {"id": 2, "name": "Молоко ультрапастеризованное 3.2%", "category": "Молочная продукция", "unit": "л", "package_quantity": 1.0, "package_unit": "л", "current_stock": 12.0, "minimum_stock": 25.0},
        {"id": 3, "name": "Сироп Ваниль 1л", "category": "Сиропы и топпинги", "unit": "бут", "package_quantity": 1.0, "package_unit": "бут", "current_stock": 4.0, "minimum_stock": 5.0},
        {"id": 4, "name": "Сироп Карамель 1л", "category": "Сиропы и топпинги", "unit": "бут", "package_quantity": 1.0, "package_unit": "бут", "current_stock": 7.0, "minimum_stock": 5.0},
        {"id": 5, "name": "Стаканы бумажные двухслойные 350мл (50 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 50.0, "package_unit": "шт", "current_stock": 14.0, "minimum_stock": 10.0},
        {"id": 6, "name": "Крышки для стаканов 80мм (100 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 100.0, "package_unit": "шт", "current_stock": 8.0, "minimum_stock": 10.0},
        {"id": 7, "name": "Салфетки барные 24x24 (400 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 400.0, "package_unit": "шт", "current_stock": 12.0, "minimum_stock": 8.0},
        {"id": 8, "name": "Трубочки биоразлагаемые (200 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 200.0, "package_unit": "шт", "current_stock": 9.0, "minimum_stock": 5.0},
        {"id": 9, "name": "Чай листовой черный Ассам", "category": "Чай", "unit": "кг", "package_quantity": 1.0, "package_unit": "кг", "current_stock": 3.5, "minimum_stock": 2.0},
        {"id": 10, "name": "Чай зеленый Сенча", "category": "Чай", "unit": "кг", "package_quantity": 1.0, "package_unit": "кг", "current_stock": 2.5, "minimum_stock": 2.0},
    ]
    for p in products1_data:
        db.add(Product(
            id=p["id"], organization_id=org1.id, name=p["name"], category=p["category"],
            unit=p["unit"], package_quantity=p["package_quantity"], package_unit=p["package_unit"],
            current_stock=p["current_stock"], minimum_stock=p["minimum_stock"],
            created_at=datetime(2026, 6, 1, 10, 0, 0)
        ))
    db.flush()

    batch_fin1 = ImportBatch(
        id=1, organization_id=org1.id, file_name="legacy_finances.xlsx", import_type="finances",
        status="success", rows_total=53, rows_imported=53, rows_skipped=0,
        error_summary="Успешно импортированы исторические транзакции кофейни за 4 месяца",
        created_at=datetime(2026, 10, 10, 14, 20, 0)
    )
    batch_purch1 = ImportBatch(
        id=2, organization_id=org1.id, file_name="legacy_purchases.xlsx", import_type="purchases",
        status="success", rows_total=31, rows_imported=31, rows_skipped=0,
        error_summary="Успешно импортирована история закупок сырья и расходников",
        created_at=datetime(2026, 10, 10, 14, 22, 0)
    )
    db.add(batch_fin1)
    db.add(batch_purch1)
    db.flush()

    # Purchases for Org 1 (Coffee Spike to 11 500 ₸)
    purchases1_records = [
        # Coffee (id 1) from Coffee Roasters Hub (id 1)
        (1, 1, today - timedelta(days=85), 25.0, "кг", 10000.0, 250000.0),
        (1, 1, today - timedelta(days=55), 25.0, "кг", 10000.0, 250000.0),
        (1, 1, today - timedelta(days=28), 25.0, "кг", 10000.0, 250000.0),
        (1, 1, today - timedelta(days=6), 25.0, "кг", 11500.0, 287500.0),  # Recent Spike +15%
        # Milk (id 2) from Almaty Dairy Group (id 5)
        (2, 5, today - timedelta(days=95), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=80), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=65), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=50), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=35), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=20), 120.0, "л", 480.0, 57600.0),
        (2, 5, today - timedelta(days=5), 120.0, "л", 480.0, 57600.0),
        # Syrups (id 3, 4) from Barista Pro (id 7)
        (3, 7, today - timedelta(days=75), 6.0, "бут", 3900.0, 23400.0),
        (4, 7, today - timedelta(days=75), 6.0, "бут", 3900.0, 23400.0),
        (3, 7, today - timedelta(days=40), 6.0, "бут", 3900.0, 23400.0),
        (4, 7, today - timedelta(days=40), 6.0, "бут", 3900.0, 23400.0),
        (3, 7, today - timedelta(days=12), 6.0, "бут", 3900.0, 23400.0),
        (4, 7, today - timedelta(days=12), 6.0, "бут", 3900.0, 23400.0),
        # Packaging (id 5, 6, 7) from EcoPack Kazakhstan (id 9)
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
    for p_id, s_id, p_date, qty, unit, u_price, tot_price in purchases1_records:
        db.add(Purchase(
            organization_id=org1.id, product_id=p_id, supplier_id=s_id, purchase_date=p_date,
            quantity=qty, unit=unit, unit_price=u_price, total_price=tot_price,
            source="legacy_import", import_batch_id=batch_purch1.id,
            created_at=datetime.combine(p_date, datetime.min.time())
        ))
    db.flush()

    # Offers for Org 1
    offers1_data = [
        {"product_id": 1, "supplier_id": 2, "offered_price": 10350.0, "unit": "кг", "package_quantity": 1.0, "minimum_order_quantity": 20.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 12, 11, 0, 0)},
        {"product_id": 1, "supplier_id": 3, "offered_price": 10800.0, "unit": "кг", "package_quantity": 1.0, "minimum_order_quantity": 15.0, "delivery_cost": 1500.0, "updated_at": datetime(2026, 10, 10, 9, 30, 0)},
        {"product_id": 1, "supplier_id": 1, "offered_price": 11500.0, "unit": "кг", "package_quantity": 1.0, "minimum_order_quantity": 10.0, "delivery_cost": 2500.0, "updated_at": datetime(2026, 10, 8, 16, 0, 0)},
        {"product_id": 1, "supplier_id": 4, "offered_price": 12200.0, "unit": "кг", "package_quantity": 1.0, "minimum_order_quantity": 5.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 13, 10, 0, 0)},
        {"product_id": 2, "supplier_id": 6, "offered_price": 440.0, "unit": "л", "package_quantity": 1.0, "minimum_order_quantity": 50.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 11, 14, 0, 0)},
        {"product_id": 2, "supplier_id": 5, "offered_price": 480.0, "unit": "л", "package_quantity": 1.0, "minimum_order_quantity": 40.0, "delivery_cost": 1000.0, "updated_at": datetime(2026, 10, 9, 12, 0, 0)},
        {"product_id": 5, "supplier_id": 10, "offered_price": 1350.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 20.0, "delivery_cost": 1000.0, "updated_at": datetime(2026, 10, 9, 15, 0, 0)},
        {"product_id": 5, "supplier_id": 9, "offered_price": 1450.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 10.0, "delivery_cost": 1800.0, "updated_at": datetime(2026, 10, 7, 10, 0, 0)},
        {"product_id": 3, "supplier_id": 8, "offered_price": 3650.0, "unit": "бут", "package_quantity": 1.0, "minimum_order_quantity": 4.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 10, 10, 0, 0)},
        {"product_id": 3, "supplier_id": 7, "offered_price": 3900.0, "unit": "бут", "package_quantity": 1.0, "minimum_order_quantity": 4.0, "delivery_cost": 1200.0, "updated_at": datetime(2026, 10, 6, 11, 0, 0)},
    ]
    for o in offers1_data:
        db.add(SupplierOffer(
            organization_id=org1.id, product_id=o["product_id"], supplier_id=o["supplier_id"],
            offered_price=o["offered_price"], unit=o["unit"], package_quantity=o["package_quantity"],
            minimum_order_quantity=o["minimum_order_quantity"], delivery_cost=o["delivery_cost"],
            updated_at=o["updated_at"], source_type="mock", is_demo=True
        ))
    db.flush()

    # Financial Transactions for Org 1
    fin1_txs = []
    for offset_months, base_date in [(3, date(2026, 7, 1)), (2, date(2026, 8, 1)), (1, date(2026, 9, 1)), (0, date(2026, 10, 1))]:
        fin1_txs.append((base_date.replace(day=5), "Аренда помещения кофейни (ул. Абая 45)", "Аренда помещения", 650000.0, "expense"))
        fin1_txs.append((base_date.replace(day=10), "Аванс заработной платы бариста и смене", "Фонд оплаты труда", 425000.0, "expense"))
        fin1_txs.append((base_date.replace(day=25), "Окончательный расчет по ЗП", "Фонд оплаты труда", 425000.0, "expense"))
        fin1_txs.append((base_date.replace(day=15), "Коммунальные услуги и электроэнергия", "Коммунальные услуги", 92000.0 + offset_months * 1800, "expense"))
        fin1_txs.append((base_date.replace(day=18), "ТО и чистка эспрессо-машины Nuova Simonelli", "Обслуживание оборудования", 45000.0, "expense"))

    fin1_txs.append((today - timedelta(days=85), "Закупка кофе в зернах Espresso Blend (25 кг)", "Закупка кофе", 250000.0, "expense"))
    fin1_txs.append((today - timedelta(days=55), "Закупка кофе в зернах Espresso Blend (25 кг)", "Закупка кофе", 250000.0, "expense"))
    fin1_txs.append((today - timedelta(days=28), "Закупка кофе в зернах Espresso Blend (25 кг)", "Закупка кофе", 250000.0, "expense"))
    fin1_txs.append((today - timedelta(days=6), "Закупка кофе в зернах Espresso Blend (25 кг по новой цене)", "Закупка кофе", 287500.0, "expense"))

    for days_ago in [95, 80, 65, 50, 35, 20, 5]:
        fin1_txs.append((today - timedelta(days=days_ago), "Закупка ультрапастеризованного молока 3.2% (120 л)", "Закупка молока и продуктов", 57600.0, "expense"))
    for days_ago in [90, 60, 30, 8]:
        fin1_txs.append((today - timedelta(days=days_ago), "Заказ стаканов 350мл, крышек и барных салфеток", "Расходные материалы", 78500.0, "expense"))
    for days_ago in [75, 40, 12]:
        fin1_txs.append((today - timedelta(days=days_ago), "Пополнение запаса сиропов (Ваниль, Карамель) и листового чая", "Закупка молока и продуктов", 42000.0, "expense"))

    for i in range(15):
        dt = today - timedelta(days=i * 7 + 2)
        fin1_txs.append((dt, "Выручка кофейни за неделю (касса + безналичный эквайринг)", "Выручка / Продажи", 710000.0 + (i % 3) * 35000, "income"))

    for t_date, desc, cat, amt, t_type in fin1_txs:
        db.add(FinancialTransaction(
            organization_id=org1.id, transaction_date=t_date, description=desc, category=cat,
            amount=amt, transaction_type=t_type, source="legacy_import", import_batch_id=batch_fin1.id,
            created_at=datetime.combine(t_date, datetime.min.time())
        ))
    db.flush()

    # Notifications for Org 1
    notifs1_data = [
        {"title": "Повышение цены на кофе +15.0%", "description": "Поставщик Coffee Roasters Hub повысил цену на «Кофе в зернах Espresso Blend 100% Арабика» с 10 000 ₸ до 11 500 ₸/кг (+1 500 ₸ за ед.).", "severity": "danger", "notification_type": "price_spike", "related_product_id": 1, "created_at": datetime.combine(today - timedelta(days=6), datetime.min.time()) + timedelta(hours=14)},
        {"title": "Обнаружено альтернативное предложение по кофе", "description": "Поставщик Aroma Direct предлагает сопоставимый товар за 10 350 ₸/кг. Потенциальная разница — 1 150 ₸/кг (до 23 000 ₸ на партию 20 кг).", "severity": "success", "notification_type": "alternative_offer", "related_product_id": 1, "created_at": datetime.combine(today - timedelta(days=2), datetime.min.time()) + timedelta(hours=11)},
        {"title": "Критический остаток: молоко 3.2%", "description": "Текущий остаток молока составляет 12 л при минимальном пороге 25 л. При среднем потреблении 8 л/день запаса хватит на 1.5 дня.", "severity": "warning", "notification_type": "low_stock", "related_product_id": 2, "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)},
        {"title": "Заканчиваются крышки для стаканов 80мм", "description": "Остаток «Крышки для стаканов 80мм» — 8 упак при минимальном запасе 10 упак. Рекомендуется включить в ближайший заказ.", "severity": "warning", "notification_type": "low_stock", "related_product_id": 6, "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()) + timedelta(hours=16)},
        {"title": "Рост расходов в категории «Закупка кофе»", "description": "Расходы на кофе в октябре выросли на 15.0% из-за изменения базового тарифа поставщика.", "severity": "info", "notification_type": "expense_change", "related_product_id": 1, "created_at": datetime.combine(today, datetime.min.time()) + timedelta(hours=8)},
    ]
    for n in notifs1_data:
        db.add(Notification(
            organization_id=org1.id, title=n["title"], description=n["description"],
            severity=n["severity"], notification_type=n["notification_type"],
            related_product_id=n["related_product_id"], is_read=False, created_at=n["created_at"]
        ))
    db.flush()

    # =========================================================================
    # ORGANIZATION 2: DAILY CUP (Regular Long-Time Usage Scenario)
    # =========================================================================
    org2 = Organization(
        id=2,
        name="Сеть кофеен «Daily Cup»",
        business_type="Кофейня формата To-Go",
        created_at=datetime(2026, 4, 15, 9, 0, 0),
    )
    db.add(org2)
    db.flush()

    user2 = User(
        id=2,
        organization_id=org2.id,
        name="Данияр Касымов",
        email="dailycup@bizmind.kz",
        role="Операционный директор / Владелец",
        created_at=datetime(2026, 4, 15, 9, 30, 0),
    )
    db.add(user2)
    db.flush()

    # Suppliers for Org 2 (IDs 101-110)
    suppliers2_data = [
        {"id": 101, "name": "PackGroup Almaty", "contact_name": "Бахыт Касым (+7 701 321-45-67)", "delivery_cost": 1500.0, "minimum_order_amount": 20000.0, "source_type": "manual", "is_demo": True},
        {"id": 102, "name": "EcoTorg Kazakhstan", "contact_name": "Жандос Сарсенов (+7 778 112-23-34)", "delivery_cost": 0.0, "minimum_order_amount": 15000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 103, "name": "Almaty HoReCa Box", "contact_name": "Отдел поставок упаковки (+7 727 255-40-10)", "delivery_cost": 1000.0, "minimum_order_amount": 25000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 104, "name": "Silk Road Coffee Trading", "contact_name": "Рустам Асанов (+7 702 999-88-77)", "delivery_cost": 0.0, "minimum_order_amount": 30000.0, "source_type": "manual", "is_demo": True},
        {"id": 105, "name": "Parmalat Distribution KZ", "contact_name": "Логистический центр (+7 705 333-55-11)", "delivery_cost": 1200.0, "minimum_order_amount": 20000.0, "source_type": "manual", "is_demo": True},
        {"id": 106, "name": "Healthy Drinks Almaty", "contact_name": "Гульнара Бек (+7 707 555-44-33)", "delivery_cost": 1200.0, "minimum_order_amount": 10000.0, "source_type": "manual", "is_demo": True},
        {"id": 107, "name": "BioMilk Almaty", "contact_name": "Оптовый склад эко-продуктов (+7 708 777-66-55)", "delivery_cost": 0.0, "minimum_order_amount": 15000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 108, "name": "Syrup Master KZ", "contact_name": "Кирилл Левин (+7 700 444-33-22)", "delivery_cost": 1000.0, "minimum_order_amount": 15000.0, "source_type": "manual", "is_demo": True},
        {"id": 109, "name": "Syrup Direct", "contact_name": "Ербол Мусин (+7 775 888-99-00)", "delivery_cost": 0.0, "minimum_order_amount": 12000.0, "source_type": "mock_catalog", "is_demo": True},
        {"id": 110, "name": "Bake & Sweet Almaty", "contact_name": "Цех выпечки (+7 701 777-12-34)", "delivery_cost": 1500.0, "minimum_order_amount": 20000.0, "source_type": "manual", "is_demo": True},
    ]
    for s in suppliers2_data:
        db.add(Supplier(
            id=s["id"], organization_id=org2.id, name=s["name"], contact_name=s["contact_name"],
            delivery_cost=s["delivery_cost"], minimum_order_amount=s["minimum_order_amount"],
            source_type=s["source_type"], is_demo=s["is_demo"]
        ))
    db.flush()

    # Products for Org 2 (IDs 101-110)
    products2_data = [
        {"id": 101, "name": "Стаканы двухслойные 250мл Kraft (50 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 50.0, "package_unit": "шт", "current_stock": 15.0, "minimum_stock": 20.0},
        {"id": 102, "name": "Стаканы двухслойные 350мл Kraft (50 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 50.0, "package_unit": "шт", "current_stock": 25.0, "minimum_stock": 20.0},
        {"id": 103, "name": "Крышки черные для стаканов 80мм (100 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 100.0, "package_unit": "шт", "current_stock": 18.0, "minimum_stock": 15.0},
        {"id": 104, "name": "Держатели для 2 стаканов (100 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 100.0, "package_unit": "шт", "current_stock": 6.0, "minimum_stock": 12.0},  # Critical!
        {"id": 105, "name": "Кофе в зернах Daily Blend (80% Арабика, 20% Робуста)", "category": "Кофе", "unit": "кг", "package_quantity": 1.0, "package_unit": "кг", "current_stock": 35.0, "minimum_stock": 25.0},
        {"id": 106, "name": "Молоко бариста 3.2% Parmalat", "category": "Молочная продукция", "unit": "л", "package_quantity": 1.0, "package_unit": "л", "current_stock": 60.0, "minimum_stock": 40.0},
        {"id": 107, "name": "Растительное овсяное молоко Alpro Barista", "category": "Молочная продукция", "unit": "л", "package_quantity": 1.0, "package_unit": "л", "current_stock": 8.0, "minimum_stock": 15.0},  # Low!
        {"id": 108, "name": "Сироп Соленая карамель 1л Monin", "category": "Сиропы и топпинги", "unit": "бут", "package_quantity": 1.0, "package_unit": "бут", "current_stock": 3.0, "minimum_stock": 5.0},  # Low!
        {"id": 109, "name": "Сироп Лесной орех 1л Monin", "category": "Сиропы и топпинги", "unit": "бут", "package_quantity": 1.0, "package_unit": "бут", "current_stock": 4.0, "minimum_stock": 5.0},
        {"id": 110, "name": "Печенье Американо шоколадное (шоу-бокс 24 шт)", "category": "Выпечка и десерты", "unit": "бокс", "package_quantity": 24.0, "package_unit": "шт", "current_stock": 5.0, "minimum_stock": 4.0},
    ]
    for p in products2_data:
        db.add(Product(
            id=p["id"], organization_id=org2.id, name=p["name"], category=p["category"],
            unit=p["unit"], package_quantity=p["package_quantity"], package_unit=p["package_unit"],
            current_stock=p["current_stock"], minimum_stock=p["minimum_stock"],
            created_at=datetime(2026, 5, 1, 10, 0, 0)
        ))
    db.flush()

    batch_fin2 = ImportBatch(
        id=101, organization_id=org2.id, file_name="dailycup_finances.xlsx", import_type="finances",
        status="success", rows_total=48, rows_imported=48, rows_skipped=0,
        error_summary="Успешный импорт операционного журнала Daily Cup за 5 месяцев",
        created_at=datetime(2026, 10, 11, 12, 10, 0)
    )
    batch_purch2 = ImportBatch(
        id=102, organization_id=org2.id, file_name="dailycup_purchases.xlsx", import_type="purchases",
        status="success", rows_total=24, rows_imported=24, rows_skipped=0,
        error_summary="Регулярный импорт заказов упаковки, молока и зерна",
        created_at=datetime(2026, 10, 11, 12, 15, 0)
    )
    db.add(batch_fin2)
    db.add(batch_purch2)
    db.flush()

    # Purchases for Org 2 (Kraft cups 250ml jump +18.3%: 1200 -> 1420 ₸)
    purchases2_records = [
        # Kraft cups 250ml (prod 101) from PackGroup Almaty (sup 101)
        (101, 101, today - timedelta(days=115), 60.0, "упак", 1200.0, 72000.0),
        (101, 101, today - timedelta(days=85), 60.0, "упак", 1200.0, 72000.0),
        (101, 101, today - timedelta(days=55), 60.0, "упак", 1200.0, 72000.0),
        (101, 101, today - timedelta(days=25), 60.0, "упак", 1200.0, 72000.0),
        (101, 101, today - timedelta(days=4), 60.0, "упак", 1420.0, 85200.0),  # Spike +18.3%!
        # Kraft cups 350ml (prod 102) from PackGroup Almaty
        (102, 101, today - timedelta(days=115), 40.0, "упак", 1450.0, 58000.0),
        (102, 101, today - timedelta(days=75), 40.0, "упак", 1450.0, 58000.0),
        (102, 101, today - timedelta(days=35), 40.0, "упак", 1450.0, 58000.0),
        # Holders (prod 104) from PackGroup Almaty
        (104, 101, today - timedelta(days=100), 20.0, "упак", 850.0, 17000.0),
        (104, 101, today - timedelta(days=50), 20.0, "упак", 850.0, 17000.0),
        (104, 101, today - timedelta(days=10), 20.0, "упак", 850.0, 17000.0),
        # Coffee Daily Blend (prod 105) from Silk Road Coffee (sup 104)
        (105, 104, today - timedelta(days=110), 40.0, "кг", 8200.0, 328000.0),
        (105, 104, today - timedelta(days=80), 40.0, "кг", 8200.0, 328000.0),
        (105, 104, today - timedelta(days=50), 40.0, "кг", 8200.0, 328000.0),
        (105, 104, today - timedelta(days=20), 40.0, "кг", 8200.0, 328000.0),
        # Parmalat Milk (prod 106) from Parmalat Distribution (sup 105)
        (106, 105, today - timedelta(days=120), 150.0, "л", 520.0, 78000.0),
        (106, 105, today - timedelta(days=90), 150.0, "л", 520.0, 78000.0),
        (106, 105, today - timedelta(days=60), 150.0, "л", 520.0, 78000.0),
        (106, 105, today - timedelta(days=30), 150.0, "л", 520.0, 78000.0),
        (106, 105, today - timedelta(days=5), 150.0, "л", 520.0, 78000.0),
        # Oat milk Alpro (prod 107) from Healthy Drinks Almaty (sup 106)
        (107, 106, today - timedelta(days=90), 20.0, "л", 1150.0, 23000.0),
        (107, 106, today - timedelta(days=45), 20.0, "л", 1150.0, 23000.0),
        (107, 106, today - timedelta(days=8), 20.0, "л", 1150.0, 23000.0),
        # Monin Caramel Syrup (prod 108) from Syrup Master KZ (sup 108)
        (108, 108, today - timedelta(days=90), 8.0, "бут", 4600.0, 36800.0),
        (108, 108, today - timedelta(days=30), 8.0, "бут", 4600.0, 36800.0),
    ]
    for p_id, s_id, p_date, qty, unit, u_price, tot_price in purchases2_records:
        db.add(Purchase(
            organization_id=org2.id, product_id=p_id, supplier_id=s_id, purchase_date=p_date,
            quantity=qty, unit=unit, unit_price=u_price, total_price=tot_price,
            source="regular_system", import_batch_id=batch_purch2.id,
            created_at=datetime.combine(p_date, datetime.min.time())
        ))
    db.flush()

    # Offers for Org 2
    offers2_data = [
        # Kraft cups 250ml (prod 101): Current PackGroup 1420 ₸ vs EcoTorg 1230 ₸ (-190 ₸/pack savings, free shipping!)
        {"product_id": 101, "supplier_id": 102, "offered_price": 1230.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 30.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 12, 10, 0, 0)},
        {"product_id": 101, "supplier_id": 103, "offered_price": 1290.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 20.0, "delivery_cost": 1000.0, "updated_at": datetime(2026, 10, 11, 14, 0, 0)},
        {"product_id": 101, "supplier_id": 101, "offered_price": 1420.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 20.0, "delivery_cost": 1500.0, "updated_at": datetime(2026, 10, 10, 9, 0, 0)},
        # Holders (prod 104): PackGroup 850 ₸ vs EcoTorg 790 ₸ (-60 ₸/pack)
        {"product_id": 104, "supplier_id": 102, "offered_price": 790.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 10.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 9, 11, 0, 0)},
        {"product_id": 104, "supplier_id": 101, "offered_price": 850.0, "unit": "упак", "package_quantity": 1.0, "minimum_order_quantity": 10.0, "delivery_cost": 1500.0, "updated_at": datetime(2026, 10, 8, 15, 0, 0)},
        # Oat milk (prod 107): Healthy Drinks 1150 ₸ vs BioMilk 1080 ₸ (-70 ₸/л)
        {"product_id": 107, "supplier_id": 107, "offered_price": 1080.0, "unit": "л", "package_quantity": 1.0, "minimum_order_quantity": 12.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 12, 16, 0, 0)},
        {"product_id": 107, "supplier_id": 106, "offered_price": 1150.0, "unit": "л", "package_quantity": 1.0, "minimum_order_quantity": 10.0, "delivery_cost": 1200.0, "updated_at": datetime(2026, 10, 7, 12, 0, 0)},
        # Caramel Syrup (prod 108): Syrup Master 4600 ₸ vs Syrup Direct 4350 ₸ (-250 ₸/бут)
        {"product_id": 108, "supplier_id": 109, "offered_price": 4350.0, "unit": "бут", "package_quantity": 1.0, "minimum_order_quantity": 4.0, "delivery_cost": 0.0, "updated_at": datetime(2026, 10, 10, 13, 0, 0)},
        {"product_id": 108, "supplier_id": 108, "offered_price": 4600.0, "unit": "бут", "package_quantity": 1.0, "minimum_order_quantity": 4.0, "delivery_cost": 1000.0, "updated_at": datetime(2026, 10, 6, 11, 0, 0)},
    ]
    for o in offers2_data:
        db.add(SupplierOffer(
            organization_id=org2.id, product_id=o["product_id"], supplier_id=o["supplier_id"],
            offered_price=o["offered_price"], unit=o["unit"], package_quantity=o["package_quantity"],
            minimum_order_quantity=o["minimum_order_quantity"], delivery_cost=o["delivery_cost"],
            updated_at=o["updated_at"], source_type="mock", is_demo=True
        ))
    db.flush()

    # Financial Transactions for Org 2 (5 months)
    fin2_txs = []
    for month_offset in [120, 90, 60, 30, 2]:
        dt = today - timedelta(days=month_offset)
        fin2_txs.append((dt.replace(day=3), "Аренда помещения Daily Cup To-Go (ул. Достык 89)", "Аренда помещения", 850000.0, "expense"))
        fin2_txs.append((dt.replace(day=10), "Аванс заработной платы смены бариста", "Фонд оплаты труда", 480000.0, "expense"))
        fin2_txs.append((dt.replace(day=25), "Расчет заработной платы бариста и клининг", "Фонд оплаты труда", 480000.0, "expense"))
        fin2_txs.append((dt.replace(day=14), "Коммунальные платежи и охрана точки", "Коммунальные услуги", 110000.0 + (month_offset % 4) * 3200, "expense"))

    # Kraft cups purchases
    for days_ago, price in [(115, 1200.0), (85, 1200.0), (55, 1200.0), (25, 1200.0)]:
        fin2_txs.append((today - timedelta(days=days_ago), "Закупка крафтовых стаканов 250мл (60 упак)", "Расходные материалы", 72000.0, "expense"))
    fin2_txs.append((today - timedelta(days=4), "Закупка крафтовых стаканов 250мл (60 упак по новой цене 1 420 ₸)", "Расходные материалы", 85200.0, "expense"))

    # Coffee Daily Blend
    for days_ago in [110, 80, 50, 20]:
        fin2_txs.append((today - timedelta(days=days_ago), "Закупка кофе Daily Blend 80/20 (40 кг)", "Закупка кофе", 328000.0, "expense"))

    # Milk & Dairy
    for days_ago in [120, 90, 60, 30, 5]:
        fin2_txs.append((today - timedelta(days=days_ago), "Поставка молока Parmalat Barista 3.2% (150 л)", "Закупка молока и продуктов", 78000.0, "expense"))

    # Incomes (Weekly Revenues Daily Cup)
    for i in range(20):
        dt = today - timedelta(days=i * 7 + 1)
        fin2_txs.append((dt, "Еженедельная выручка точки Daily Cup Достык", "Выручка / Продажи", 980000.0 + (i % 5) * 40000, "income"))

    for t_date, desc, cat, amt, t_type in fin2_txs:
        db.add(FinancialTransaction(
            organization_id=org2.id, transaction_date=t_date, description=desc, category=cat,
            amount=amt, transaction_type=t_type, source="regular_system", import_batch_id=batch_fin2.id,
            created_at=datetime.combine(t_date, datetime.min.time())
        ))
    db.flush()

    # Notifications for Org 2
    notifs2_data = [
        {"title": "Повышение цены на стаканы 250мл Kraft +18.3%", "description": "Поставщик PackGroup Almaty повысил отпускную цену с 1 200 ₸ до 1 420 ₸/упак (+220 ₸/упак, +18.3%).", "severity": "danger", "notification_type": "price_spike", "related_product_id": 101, "created_at": datetime.combine(today - timedelta(days=4), datetime.min.time()) + timedelta(hours=15)},
        {"title": "Альтернативное предложение: EcoTorg Kazakhstan", "description": "Поставщик EcoTorg предлагает сопоставимые двухслойные стаканы по 1 230 ₸/упак с бесплатной доставкой. Потенциальная разница — 190 ₸/упак (до 11 400 ₸ на заказ 60 упак).", "severity": "success", "notification_type": "alternative_offer", "related_product_id": 101, "created_at": datetime.combine(today - timedelta(days=2), datetime.min.time()) + timedelta(hours=10)},
        {"title": "Критический остаток: Держатели для 2 стаканов", "description": "Остаток держателей — всего 6 упак при минимальной норме 12 упак. При среднем расходе запаса хватит менее чем на 2 дня.", "severity": "warning", "notification_type": "low_stock", "related_product_id": 104, "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)},
        {"title": "Запас на исходе: овсяное молоко Alpro Barista", "description": "Текущий остаток 8 л при минимуме 15 л. Рекомендуется включить в ближайший заказ растительного сырья.", "severity": "warning", "notification_type": "low_stock", "related_product_id": 107, "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()) + timedelta(hours=17)},
        {"title": "Рост расходов на расходные материалы", "description": "Расходы на одноразовую посуду в текущем месяце выросли на 18.3% из-за повышения цен поставщика.", "severity": "info", "notification_type": "expense_change", "related_product_id": 101, "created_at": datetime.combine(today, datetime.min.time()) + timedelta(hours=8)},
    ]
    for n in notifs2_data:
        db.add(Notification(
            organization_id=org2.id, title=n["title"], description=n["description"],
            severity=n["severity"], notification_type=n["notification_type"],
            related_product_id=n["related_product_id"], is_read=False, created_at=n["created_at"]
        ))
    db.commit()

    return {
        "status": "success",
        "message": "Оба демонстрационных пространства (Cafe Aroma и Daily Cup) успешно инициализированы",
        "organizations": [
            {"id": 1, "name": org1.name, "products": len(products1_data), "transactions": len(fin1_txs)},
            {"id": 2, "name": org2.name, "products": len(products2_data), "transactions": len(fin2_txs)},
        ]
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = reset_and_seed_db(db)
        print("Seed result:", res)
    finally:
        db.close()
