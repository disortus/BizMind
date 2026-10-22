import json
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models.models import (
    Organization,
    User,
    Product,
    Supplier,
    Purchase,
    PurchaseOrder,
    PurchaseOrderItem,
    SupplierOffer,
    OfferPriceHistory,
    InventoryMovement,
    FinancialTransaction,
    Notification,
    ImportBatch,
    ReportTemplate,
    ActivityLog,
)


def reset_and_seed_db(db: Session) -> Dict[str, Any]:
    """
    Deterministically recreates database state with:
    1. Global Shared Supplier Catalog (accessible to all organizations)
    2. System Preset Report Templates (accessible to all organizations)
    3. Scenario A (Cafe Aroma): Pure, clean initial onboarding state (0 transactions, 0 purchases, 0 inventory).
    4. Scenario B (Daily Cup): Mature 6-month historical usage dataset with proven realized savings.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    today = date(2026, 10, 14)

    # =========================================================================
    # 0. SYSTEM PRESET REPORT TEMPLATES
    # =========================================================================
    preset_templates = [
        {
            "id": 1,
            "title": "Ежемесячный финансовый отчёт",
            "report_type": "financial",
            "description": "Анализ доходов, структуры операционных расходов и чистой прибыли кафе по категориям",
            "config": {
                "title": "Ежемесячный финансовый отчёт",
                "sections": ["kpi_summary", "category_breakdown", "dynamics_chart", "detailed_table"],
                "period_type": "current_month",
                "group_by": "category",
                "sort_by": "amount_desc",
            },
        },
        {
            "id": 2,
            "title": "Анализ закупок и изменения цен",
            "report_type": "procurement",
            "description": "Сводка по поставкам сырья и расходников, динамика цен и расчет подтвержденной экономии",
            "config": {
                "title": "Анализ закупок и изменения цен",
                "sections": ["kpi_summary", "supplier_distribution", "price_changes", "detailed_table"],
                "period_type": "last_90d",
                "group_by": "supplier",
                "sort_by": "amount_desc",
            },
        },
        {
            "id": 3,
            "title": "Склад и низкие остатки",
            "report_type": "inventory",
            "description": "Мониторинг фактических остатков сырья, выявление дефицита и расчет стоимости запасов",
            "config": {
                "title": "Склад и низкие остатки",
                "sections": ["kpi_summary", "low_stock_table", "inventory_movements"],
                "period_type": "current_month",
                "group_by": "category",
                "sort_by": "stock_asc",
            },
        },
        {
            "id": 4,
            "title": "Сводный отчёт владельца кафе",
            "report_type": "executive",
            "description": "Комплексный управленческий дашборд: выручка, расходы, маржинальность, статус склада и эффект BizMind",
            "config": {
                "title": "Сводный отчёт владельца кафе",
                "sections": ["kpi_summary", "category_breakdown", "procurement_kpi", "stock_kpi", "savings_kpi"],
                "period_type": "last_30d",
                "group_by": "category",
                "sort_by": "amount_desc",
            },
        },
    ]

    for pt in preset_templates:
        db.add(
            ReportTemplate(
                id=pt["id"],
                organization_id=None,
                title=pt["title"],
                description=pt["description"],
                report_type=pt["report_type"],
                config=json.dumps(pt["config"], ensure_ascii=False),
                is_system=True,
                is_archived=False,
                created_at=datetime(2026, 4, 1, 9, 0, 0),
                updated_at=datetime(2026, 4, 1, 9, 0, 0),
            )
        )
    db.flush()

    # =========================================================================
    # 1. GLOBAL SHARED SUPPLIER CATALOG (Общая демонстрационная база BizMind)
    # =========================================================================
    global_suppliers_data = [
        {
            "id": 1001,
            "name": "Global Coffee Roasters Hub",
            "contact_name": "Единый склад обжарки (+7 701 555-00-11)",
            "phone": "+7 701 555-00-11",
            "email": "roasters@bizmind-catalog.kz",
            "address": "г. Алматы, пр. Райымбека 212",
            "delivery_cost": 2500.0,
            "minimum_order_amount": 30000.0,
            "notes": "Общая база BizMind: поставщик свежеобжаренного кофе (100% Арабика, эспрессо-смеси, моносорта)",
            "source_type": "global",
            "is_global": True,
            "is_demo": True,
            "is_active": True,
        },
        {
            "id": 1002,
            "name": "Qazaq Milk Line",
            "contact_name": "Менеджер оптовых поставок (+7 707 988-77-66)",
            "phone": "+7 707 988-77-66",
            "email": "milk@bizmind-catalog.kz",
            "address": "г. Алматы, ул. Жандосова 98",
            "delivery_cost": 0.0,
            "minimum_order_amount": 20000.0,
            "notes": "Общая база BizMind: натуральное молоко 3.2%, безлактозное и растительное молоко для бариста",
            "source_type": "global",
            "is_global": True,
            "is_demo": True,
            "is_active": True,
        },
        {
            "id": 1003,
            "name": "SweetSyrup Co",
            "contact_name": "Отдел кондитерских сиропов (+7 701 444-55-66)",
            "phone": "+7 701 444-55-66",
            "email": "syrups@bizmind-catalog.kz",
            "address": "г. Алматы, ул. Толе би 180",
            "delivery_cost": 0.0,
            "minimum_order_amount": 15000.0,
            "notes": "Общая база BizMind: профессиональные барные сиропы (карамель, ваниль, фундук) и топпинги",
            "source_type": "global",
            "is_global": True,
            "is_demo": True,
            "is_active": True,
        },
        {
            "id": 1004,
            "name": "EcoPack Kazakhstan",
            "contact_name": "Склад упаковки HoReCa (+7 777 654-32-10)",
            "phone": "+7 777 654-32-10",
            "email": "ecopack@bizmind-catalog.kz",
            "address": "г. Алматы, ул. Сатпаева 30",
            "delivery_cost": 1800.0,
            "minimum_order_amount": 20000.0,
            "notes": "Общая база BizMind: двухслойные крафтовые стаканы, крышки, переноски, салфетки и трубочки",
            "source_type": "global",
            "is_global": True,
            "is_demo": True,
            "is_active": True,
        },
        {
            "id": 1005,
            "name": "CleanService HoReCa",
            "contact_name": "Служба снабжения (+7 700 123-45-67)",
            "phone": "+7 700 123-45-67",
            "email": "clean@bizmind-catalog.kz",
            "address": "г. Алматы, ул. Розыбакиева 111",
            "delivery_cost": 1000.0,
            "minimum_order_amount": 10000.0,
            "notes": "Общая база BizMind: профессиональная химия для кофемашин, дезинфицирующие средства, инвентарь",
            "source_type": "global",
            "is_global": True,
            "is_demo": True,
            "is_active": True,
        },
    ]

    for gs in global_suppliers_data:
        db.add(
            Supplier(
                id=gs["id"],
                organization_id=None,
                name=gs["name"],
                contact_name=gs["contact_name"],
                phone=gs["phone"],
                email=gs["email"],
                address=gs["address"],
                delivery_cost=gs["delivery_cost"],
                minimum_order_amount=gs["minimum_order_amount"],
                notes=gs["notes"],
                source_type=gs["source_type"],
                is_global=gs["is_global"],
                is_demo=gs["is_demo"],
                is_active=gs["is_active"],
            )
        )
    db.flush()

    # =========================================================================
    # 2. SCENARIO A: CAFE AROMA (Первоначальное внедрение — ЧИСТОЕ СОСТОЯНИЕ)
    # =========================================================================
    # Cafe Aroma has just adopted BizMind. It was an existing working cafe,
    # but NO historical data has been imported into BizMind yet!
    # Therefore: 0 transactions, 0 purchases, 0 products, 0 movements, 0 notifications.
    # The user progressively imports historical Excel files.
    org1 = Organization(
        id=1,
        name="Кофейня «Cafe Aroma»",
        business_type="Кофейня / Общепит",
        currency="₸",
        alert_threshold_percent=5.0,
        address="г. Алматы, пр. Абая 45",
        phone="+7 727 345-67-89",
        email="contact@cafearoma.kz",
        created_at=datetime(2026, 5, 1, 9, 0, 0),
    )
    db.add(org1)
    db.flush()

    user1 = User(
        id=1,
        organization_id=org1.id,
        name="Алексей Смирнов",
        email="demo@bizmind.kz",
        role="owner",
        created_at=datetime(2026, 5, 1, 9, 30, 0),
    )
    user1_2 = User(
        id=12,
        organization_id=org1.id,
        name="Айгерим Садыкова",
        email="manager@cafearoma.kz",
        role="manager",
        created_at=datetime(2026, 5, 2, 10, 0, 0),
    )
    user1_3 = User(
        id=13,
        organization_id=org1.id,
        name="Ернар Бектур",
        email="barista@cafearoma.kz",
        role="employee",
        created_at=datetime(2026, 5, 3, 11, 0, 0),
    )
    db.add_all([user1, user1_2, user1_3])
    db.flush()

    # Initial activity logs for Org 1 (Cafe Aroma)
    db.add_all([
        ActivityLog(
            organization_id=org1.id,
            user_id=user1.id,
            user_name=user1.name,
            action="SYSTEM_INIT",
            entity_type="Organization",
            entity_id=str(org1.id),
            details="Регистрация демонстрационного пространства кофейни «Cafe Aroma»",
            created_at=datetime(2026, 5, 1, 9, 15, 0),
        ),
        ActivityLog(
            organization_id=org1.id,
            user_id=user1.id,
            user_name=user1.name,
            action="SECURITY_SETUP",
            entity_type="Security",
            entity_id="rbac",
            details="Настройка ролевого доступа сотрудников (Owner, Manager, Employee)",
            created_at=datetime(2026, 5, 3, 11, 30, 0),
        ),
    ])
    db.flush()

    # NOTE: Org 1 has NO pre-seeded transactions, purchases, products, or stock!
    # It starts completely empty to showcase real onboarding.

    # =========================================================================
    # 3. SCENARIO B: DAILY CUP (Многомесячное регулярное использование — 6 месяцев)
    # =========================================================================
    # Daily Cup has used BizMind for 6 months (May to October 2026).
    # Month 1-3 (May-July): High packaging costs (PackGroup: 1 420 ₸), coffee at 8 200 ₸, low stock incidents.
    # Month 4-6 (Aug-Oct): Switched to EcoTorg (1 230 ₸/pack, saved 34 200 ₸), negotiated coffee (7 500 ₸, saved 84 000 ₸),
    # negotiated milk (470 ₸, saved 35 000 ₸). Total verified realized savings = 153 200 ₸!
    org2 = Organization(
        id=2,
        name="Сеть кофеен «Daily Cup»",
        business_type="Кофейня формата To-Go",
        currency="₸",
        alert_threshold_percent=5.0,
        address="г. Алматы, пр. Достык 89",
        phone="+7 727 987-65-43",
        email="info@dailycup.kz",
        created_at=datetime(2026, 4, 15, 9, 0, 0),
    )
    db.add(org2)
    db.flush()

    user2 = User(
        id=2,
        organization_id=org2.id,
        name="Данияр Касымов",
        email="dailycup@bizmind.kz",
        role="owner",
        created_at=datetime(2026, 4, 15, 9, 30, 0),
    )
    user2_2 = User(
        id=22,
        organization_id=org2.id,
        name="Мадина Жумабаева",
        email="madina@dailycup.kz",
        role="manager",
        created_at=datetime(2026, 4, 16, 10, 0, 0),
    )
    user2_3 = User(
        id=23,
        organization_id=org2.id,
        name="Канат Ильясов",
        email="procurement@dailycup.kz",
        role="manager",
        created_at=datetime(2026, 4, 17, 11, 0, 0),
    )
    user2_4 = User(
        id=24,
        organization_id=org2.id,
        name="Бауржан Кусаинов",
        email="barista@dailycup.kz",
        role="employee",
        created_at=datetime(2026, 4, 18, 12, 0, 0),
    )
    db.add_all([user2, user2_2, user2_3, user2_4])
    db.flush()

    # Initial activity logs for Org 2 (Daily Cup)
    db.add_all([
        ActivityLog(
            organization_id=org2.id,
            user_id=user2.id,
            user_name=user2.name,
            action="SWITCH_SUPPLIER",
            entity_type="Supplier",
            entity_id="102",
            details="Оптимизация упаковки: смена поставщика на EcoTorg Kazakhstan (1 230 ₸/упак, подтвержденная экономия 34 200 ₸)",
            created_at=datetime(2026, 8, 1, 14, 0, 0),
        ),
        ActivityLog(
            organization_id=org2.id,
            user_id=user2_3.id,
            user_name=user2_3.name,
            action="PRICE_NEGOTIATION",
            entity_type="Price",
            entity_id="101",
            details="Согласование оптовой скидки с Coffee Roasters Almaty на зерно (7 500 ₸ вместо 8 200 ₸)",
            created_at=datetime(2026, 8, 5, 16, 30, 0),
        ),
        ActivityLog(
            organization_id=org2.id,
            user_id=user2_2.id,
            user_name=user2_2.name,
            action="INVENTORY_AUDIT",
            entity_type="Inventory",
            entity_id="q3_audit",
            details="Проведение плановой квартальной инвентаризации остатков склада (расхождений не выявлено)",
            created_at=datetime(2026, 9, 30, 18, 0, 0),
        ),
        ActivityLog(
            organization_id=org2.id,
            user_id=user2.id,
            user_name=user2.name,
            action="SECURITY_AUDIT",
            entity_type="Security",
            entity_id="audit_2026",
            details="Плановый аудит учетных записей и прав доступа сотрудников в системе BizMind",
            created_at=datetime(2026, 10, 15, 10, 0, 0),
        ),
    ])
    db.flush()

    # Suppliers for Org 2 (IDs 101-110)
    suppliers2_data = [
        {"id": 101, "name": "PackGroup Almaty", "contact_name": "Бахыт Касым (+7 701 321-45-67)", "delivery_cost": 1500.0, "minimum_order_amount": 20000.0, "source_type": "imported", "is_global": False},
        {"id": 102, "name": "EcoTorg Kazakhstan", "contact_name": "Жандос Сарсенов (+7 778 112-23-34)", "delivery_cost": 0.0, "minimum_order_amount": 15000.0, "source_type": "imported", "is_global": False},
        {"id": 103, "name": "Almaty HoReCa Box", "contact_name": "Отдел поставок упаковки (+7 727 255-40-10)", "delivery_cost": 1000.0, "minimum_order_amount": 25000.0, "source_type": "imported", "is_global": False},
        {"id": 104, "name": "Silk Road Coffee Trading", "contact_name": "Рустам Асанов (+7 702 999-88-77)", "delivery_cost": 0.0, "minimum_order_amount": 30000.0, "source_type": "imported", "is_global": False},
        {"id": 105, "name": "Parmalat Distribution KZ", "contact_name": "Логистический центр (+7 705 333-55-11)", "delivery_cost": 1200.0, "minimum_order_amount": 20000.0, "source_type": "imported", "is_global": False},
        {"id": 106, "name": "Healthy Drinks Almaty", "contact_name": "Гульнара Бек (+7 707 555-44-33)", "delivery_cost": 1200.0, "minimum_order_amount": 10000.0, "source_type": "imported", "is_global": False},
        {"id": 107, "name": "BioMilk Almaty", "contact_name": "Оптовый склад эко-продуктов (+7 708 777-66-55)", "delivery_cost": 0.0, "minimum_order_amount": 15000.0, "source_type": "imported", "is_global": False},
        {"id": 108, "name": "Syrup Master KZ", "contact_name": "Кирилл Левин (+7 700 444-33-22)", "delivery_cost": 1000.0, "minimum_order_amount": 15000.0, "source_type": "imported", "is_global": False},
        {"id": 109, "name": "Syrup Direct", "contact_name": "Ербол Мусин (+7 775 888-99-00)", "delivery_cost": 0.0, "minimum_order_amount": 12000.0, "source_type": "imported", "is_global": False},
        {"id": 110, "name": "Bake & Sweet Almaty", "contact_name": "Цех выпечки (+7 701 777-12-34)", "delivery_cost": 1500.0, "minimum_order_amount": 20000.0, "source_type": "manual", "is_global": False},
    ]
    for s in suppliers2_data:
        db.add(
            Supplier(
                id=s["id"],
                organization_id=org2.id,
                name=s["name"],
                contact_name=s["contact_name"],
                delivery_cost=s["delivery_cost"],
                minimum_order_amount=s["minimum_order_amount"],
                source_type=s["source_type"],
                is_global=s["is_global"],
                is_demo=True,
                is_active=True,
            )
        )
    db.flush()

    # Products for Daily Cup (Org 2, IDs 101-110)
    products2_data = [
        {"id": 101, "name": "Стаканы двухслойные 250мл Kraft (50 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 50.0, "package_unit": "шт", "current_stock": 25.0, "minimum_stock": 20.0},
        {"id": 102, "name": "Стаканы двухслойные 350мл Kraft (50 шт)", "category": "Упаковка и расходники", "unit": "упак", "package_quantity": 50.0, "package_unit": "шт", "current_stock": 30.0, "minimum_stock": 20.0},
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
        db.add(
            Product(
                id=p["id"],
                organization_id=org2.id,
                name=p["name"],
                category=p["category"],
                unit=p["unit"],
                package_quantity=p["package_quantity"],
                package_unit=p["package_unit"],
                current_stock=p["current_stock"],
                minimum_stock=p["minimum_stock"],
                created_at=datetime(2026, 5, 1, 10, 0, 0),
            )
        )
    db.flush()

    batch_fin2 = ImportBatch(
        id=101,
        organization_id=org2.id,
        file_name="dailycup_finances.xlsx",
        import_type="finances",
        status="success",
        rows_total=58,
        rows_imported=58,
        rows_skipped=0,
        error_summary="Успешный импорт операционного журнала Daily Cup за 6 месяцев",
        created_at=datetime(2026, 10, 11, 12, 10, 0),
    )
    batch_purch2 = ImportBatch(
        id=102,
        organization_id=org2.id,
        file_name="dailycup_purchases.xlsx",
        import_type="purchases",
        status="success",
        rows_total=25,
        rows_imported=25,
        rows_skipped=0,
        error_summary="Регулярный импорт заказов упаковки, молока и зерна",
        created_at=datetime(2026, 10, 11, 12, 15, 0),
    )
    db.add(batch_fin2)
    db.add(batch_purch2)
    db.flush()

    # 6-Month Purchases for Daily Cup (May to October 2026):
    # Demonstrating real optimization:
    # 1. Kraft Cups: May-July purchased from PackGroup at 1 420 ₸. Aug-Oct switched to EcoTorg at 1 230 ₸ (-190 ₸/pack).
    # 2. Coffee: May-July purchased at 8 200 ₸/kg. In August negotiated volume contract to 7 500 ₸/kg (-700 ₸/kg).
    # 3. Milk: May-July purchased at 520 ₸/L. In August negotiated contract to 470 ₸/L (-50 ₸/L).
    purchases2_records = [
        # --- PHASE 1 (Initial Months: May - July) ---
        # Kraft cups 250ml (prod 101) from PackGroup Almaty (sup 101) at high price 1420 ₸
        (101, 101, today - timedelta(days=150), 60.0, "упак", 1420.0, 85200.0),
        (101, 101, today - timedelta(days=120), 60.0, "упак", 1420.0, 85200.0),
        (101, 101, today - timedelta(days=90), 60.0, "упак", 1420.0, 85200.0),
        # Kraft cups 350ml (prod 102) from PackGroup Almaty
        (102, 101, today - timedelta(days=140), 40.0, "упак", 1450.0, 58000.0),
        (102, 101, today - timedelta(days=95), 40.0, "упак", 1450.0, 58000.0),
        # Coffee Daily Blend (prod 105) from Silk Road Coffee (sup 104) at 8 200 ₸
        (105, 104, today - timedelta(days=155), 40.0, "кг", 8200.0, 328000.0),
        (105, 104, today - timedelta(days=125), 40.0, "кг", 8200.0, 328000.0),
        (105, 104, today - timedelta(days=95), 40.0, "кг", 8200.0, 328000.0),
        # Parmalat Milk (prod 106) from Parmalat Distribution (sup 105) at 520 ₸
        (106, 105, today - timedelta(days=150), 150.0, "л", 520.0, 78000.0),
        (106, 105, today - timedelta(days=120), 150.0, "л", 520.0, 78000.0),
        (106, 105, today - timedelta(days=90), 150.0, "л", 520.0, 78000.0),
        # Holders (prod 104)
        (104, 101, today - timedelta(days=130), 20.0, "упак", 850.0, 17000.0),
        (104, 101, today - timedelta(days=80), 20.0, "упак", 850.0, 17000.0),

        # --- PHASE 2 (BizMind Optimization Months: August - October) ---
        # Kraft cups 250ml: SWITCHED to EcoTorg (sup 102) at 1 230 ₸ (Savings: 190 ₸/pack!)
        # 3 batches * 60 = 180 packs * 190 = 34 200 ₸ Realized Savings!
        (101, 102, today - timedelta(days=60), 60.0, "упак", 1230.0, 73800.0),
        (101, 102, today - timedelta(days=30), 60.0, "упак", 1230.0, 73800.0),
        (101, 102, today - timedelta(days=5), 60.0, "упак", 1230.0, 73800.0),
        # Kraft cups 350ml from EcoTorg at 1 380 ₸
        (102, 102, today - timedelta(days=50), 40.0, "упак", 1380.0, 55200.0),
        (102, 102, today - timedelta(days=12), 40.0, "упак", 1380.0, 55200.0),
        # Coffee Daily Blend: NEGOTIATED volume contract with Silk Road Coffee to 7 500 ₸!
        # 3 batches * 40 kg = 120 kg * 700 = 84 000 ₸ Realized Savings!
        (105, 104, today - timedelta(days=65), 40.0, "кг", 7500.0, 300000.0),
        (105, 104, today - timedelta(days=35), 40.0, "кг", 7500.0, 300000.0),
        (105, 104, today - timedelta(days=8), 40.0, "кг", 7500.0, 300000.0),
        # Milk Parmalat: NEGOTIATED wholesale rate to 470 ₸!
        # 700 L * 50 = 35 000 ₸ Realized Savings!
        (106, 105, today - timedelta(days=60), 200.0, "л", 470.0, 94000.0),
        (106, 105, today - timedelta(days=35), 250.0, "л", 470.0, 117500.0),
        (106, 105, today - timedelta(days=6), 250.0, "л", 470.0, 117500.0),
        # Oat milk Alpro (prod 107) from Healthy Drinks Almaty
        (107, 106, today - timedelta(days=45), 20.0, "л", 1150.0, 23000.0),
        (107, 106, today - timedelta(days=10), 20.0, "л", 1150.0, 23000.0),
        # Monin Syrup
        (108, 108, today - timedelta(days=40), 8.0, "бут", 4600.0, 36800.0),
        # Holders (prod 104)
        (104, 102, today - timedelta(days=35), 20.0, "упак", 790.0, 15800.0),
    ]

    for p_id, s_id, p_date, qty, unit, u_price, tot_price in purchases2_records:
        db.add(
            Purchase(
                organization_id=org2.id,
                product_id=p_id,
                supplier_id=s_id,
                purchase_date=p_date,
                quantity=qty,
                unit=unit,
                unit_price=u_price,
                total_price=tot_price,
                source="regular_system",
                import_batch_id=batch_purch2.id,
                created_at=datetime.combine(p_date, datetime.min.time()),
            )
        )
    db.flush()

    # Active Offers for Daily Cup
    offers2_data = [
        # Kraft cups 250ml: PackGroup (expensive 1420) vs EcoTorg (1230) vs Almaty Box (1290)
        {"product_id": 101, "supplier_id": 101, "price": 1420.0, "unit": "упак", "delivery": 1500.0, "moq": 20.0, "price_source": "user_import"},
        {"product_id": 101, "supplier_id": 102, "price": 1230.0, "unit": "упак", "delivery": 0.0, "moq": 30.0, "price_source": "user_import"},
        {"product_id": 101, "supplier_id": 103, "price": 1290.0, "unit": "упак", "delivery": 1000.0, "moq": 20.0, "price_source": "catalog"},
        # Coffee Daily Blend
        {"product_id": 105, "supplier_id": 104, "price": 7500.0, "unit": "кг", "delivery": 0.0, "moq": 40.0, "price_source": "user_import"},
        # Milk Parmalat
        {"product_id": 106, "supplier_id": 105, "price": 470.0, "unit": "л", "delivery": 0.0, "moq": 100.0, "price_source": "user_import"},
        # Oat milk Alpro: Healthy Drinks (1150) vs BioMilk (1080)
        {"product_id": 107, "supplier_id": 106, "price": 1150.0, "unit": "л", "delivery": 1200.0, "moq": 10.0, "price_source": "user_import"},
        {"product_id": 107, "supplier_id": 107, "price": 1080.0, "unit": "л", "delivery": 0.0, "moq": 12.0, "price_source": "catalog"},
        # Caramel Syrup: Syrup Master (4600) vs Syrup Direct (4350)
        {"product_id": 108, "supplier_id": 108, "price": 4600.0, "unit": "бут", "delivery": 1000.0, "moq": 4.0, "price_source": "user_import"},
        {"product_id": 108, "supplier_id": 109, "price": 4350.0, "unit": "бут", "delivery": 0.0, "moq": 4.0, "price_source": "catalog"},
        # Holders: PackGroup (850) vs EcoTorg (790)
        {"product_id": 104, "supplier_id": 101, "price": 850.0, "unit": "упак", "delivery": 1500.0, "moq": 10.0, "price_source": "user_import"},
        {"product_id": 104, "supplier_id": 102, "price": 790.0, "unit": "упак", "delivery": 0.0, "moq": 10.0, "price_source": "user_import"},
    ]
    for o in offers2_data:
        db.add(
            SupplierOffer(
                organization_id=org2.id,
                product_id=o["product_id"],
                supplier_id=o["supplier_id"],
                offered_price=o["price"],
                unit=o["unit"],
                delivery_cost=o["delivery"],
                minimum_order_quantity=o["moq"],
                price_source=o["price_source"],
                is_demo=True,
                is_active=True,
                updated_at=datetime(2026, 10, 10, 10, 0, 0),
            )
        )

    # Global catalog offers (available across organizations)
    global_offers = [
        {"product_id": 101, "supplier_id": 1004, "price": 1180.0, "unit": "упак", "delivery": 0.0, "moq": 20.0},
        {"product_id": 102, "supplier_id": 1004, "price": 1320.0, "unit": "упак", "delivery": 0.0, "moq": 20.0},
        {"product_id": 105, "supplier_id": 1001, "price": 7200.0, "unit": "кг", "delivery": 0.0, "moq": 30.0},
        {"product_id": 106, "supplier_id": 1002, "price": 450.0, "unit": "л", "delivery": 0.0, "moq": 50.0},
        {"product_id": 108, "supplier_id": 1003, "price": 4200.0, "unit": "бут", "delivery": 0.0, "moq": 4.0},
    ]
    for go in global_offers:
        db.add(
            SupplierOffer(
                organization_id=None,
                product_id=go["product_id"],
                supplier_id=go["supplier_id"],
                offered_price=go["price"],
                unit=go["unit"],
                delivery_cost=go["delivery"],
                minimum_order_quantity=go["moq"],
                price_source="catalog",
                is_demo=True,
                is_active=True,
                updated_at=datetime(2026, 10, 12, 12, 0, 0),
            )
        )
    db.flush()

    # Price History for Kraft cups (1 200 -> 1 420 ₸)
    db.add(
        OfferPriceHistory(
            organization_id=org2.id,
            product_id=101,
            supplier_id=101,
            old_price=1200.0,
            new_price=1420.0,
            change_percent=18.3,
            changed_at=datetime.combine(today - timedelta(days=90), datetime.min.time()),
        )
    )
    # Price History for Coffee discount (8 200 -> 7 500 ₸)
    db.add(
        OfferPriceHistory(
            organization_id=org2.id,
            product_id=105,
            supplier_id=104,
            old_price=8200.0,
            new_price=7500.0,
            change_percent=-8.5,
            changed_at=datetime.combine(today - timedelta(days=65), datetime.min.time()),
        )
    )
    db.flush()

    # Financial Transactions for Daily Cup (6 months of rent, salaries, utilities, revenues, purchases)
    fin2_txs = []
    for month_offset in [150, 120, 90, 60, 30, 2]:
        dt = today - timedelta(days=month_offset)
        # Rent
        fin2_txs.append((dt.replace(day=3), "Аренда помещения Daily Cup To-Go (ул. Достык 89)", "Аренда помещения", 850000.0, "expense"))
        # FOT
        fin2_txs.append((dt.replace(day=10), "Аванс заработной платы смены бариста", "Фонд оплаты труда", 480000.0, "expense"))
        fin2_txs.append((dt.replace(day=25), "Окончательный расчет по ЗП бариста и клининг", "Фонд оплаты труда", 480000.0, "expense"))
        # Utilities
        fin2_txs.append((dt.replace(day=14), "Коммунальные платежи и охрана точки", "Коммунальные услуги", 110000.0 + (month_offset % 4) * 3200, "expense"))

    # Include purchase expenses matching the purchase orders
    for p_id, s_id, p_date, qty, unit, u_price, tot_price in purchases2_records:
        cat = "Закупка кофе" if p_id == 105 else ("Закупка молока и продуктов" if p_id in [106, 107, 108] else "Расходные материалы")
        desc_tx = f"Оплата поставки #{s_id} ({qty} {unit})"
        fin2_txs.append((p_date, desc_tx, cat, tot_price, "expense"))

    # 24 Weekly revenues
    for i in range(24):
        dt = today - timedelta(days=i * 7 + 1)
        fin2_txs.append((dt, "Выручка кофейни To-Go за неделю (касса + QR)", "Выручка / Продажи", 820000.0 + (i % 5) * 35000, "income"))


    for t_date, desc_tx, cat, amt, t_type in fin2_txs:
        db.add(
            FinancialTransaction(
                organization_id=org2.id,
                transaction_date=t_date,
                description=desc_tx,
                category=cat,
                amount=amt,
                transaction_type=t_type,
                source="regular_system",
                import_batch_id=batch_fin2.id,
                created_at=datetime.combine(t_date, datetime.min.time()),
            )
        )
    db.flush()

    # Legitimate Notifications for Daily Cup
    notifs2_data = [
        {
            "title": "Достигнута подтвержденная экономия 153 200 ₸",
            "description": "Благодаря оптимизации закупок в BizMind: смена поставщика стаканов (34 200 ₸), скидка на кофе (84 000 ₸) и молоко (35 000 ₸).",
            "severity": "success",
            "notification_type": "expense_change",
            "related_product_id": 101,
            "created_at": datetime.combine(today - timedelta(days=5), datetime.min.time()),
        },
        {
            "title": "Критический остаток: держатели для 2 стаканов",
            "description": "Текущий остаток держателей составляет 6 упак при норме 12 упак. При среднем расходе 1 упак/день запаса хватит менее чем на 6 дней.",
            "severity": "warning",
            "notification_type": "low_stock",
            "related_product_id": 104,
            "created_at": datetime.combine(today - timedelta(days=2), datetime.min.time()),
        },
        {
            "title": "Низкий остаток: овсяное молоко Alpro Barista",
            "description": "Остаток овсяного молока — 8 л при минимальном пороге 15 л. Рекомендуется сформировать заказ у BioMilk (1 080 ₸/л).",
            "severity": "warning",
            "notification_type": "low_stock",
            "related_product_id": 107,
            "created_at": datetime.combine(today - timedelta(days=1), datetime.min.time()),
        },
        {
            "title": "Выгодное предложение: растительное молоко BioMilk",
            "description": "Поставщик BioMilk предлагает растительное молоко по 1 080 ₸/л вместо текущих 1 150 ₸/л у Healthy Drinks. Потенциал экономии — 70 ₸/л.",
            "severity": "info",
            "notification_type": "alternative_offer",
            "related_product_id": 107,
            "created_at": datetime.combine(today - timedelta(days=3), datetime.min.time()),
        },
    ]

    for n in notifs2_data:
        db.add(
            Notification(
                organization_id=org2.id,
                title=n["title"],
                description=n["description"],
                severity=n["severity"],
                notification_type=n["notification_type"],
                related_product_id=n["related_product_id"],
                is_read=False,
                created_at=n["created_at"],
            )
        )
    db.flush()

    db.commit()

    return {
        "status": "success",
        "message": "Deterministic seed completed: Cafe Aroma set to clean onboarding state, Daily Cup set to 6-month mature usage.",
        "org1_cafe_aroma": {
            "id": org1.id,
            "name": org1.name,
            "transactions_count": 0,
            "purchases_count": 0,
            "products_count": 0,
            "state": "empty_onboarding",
        },
        "org2_daily_cup": {
            "id": org2.id,
            "name": org2.name,
            "transactions_count": len(fin2_txs),
            "purchases_count": len(purchases2_records),
            "products_count": len(products2_data),
            "realized_savings_kzt": 153200.0,
            "state": "mature_6_months_history",
        },
        "global_suppliers_count": len(global_suppliers_data),
        "preset_templates_count": len(preset_templates),
    }
