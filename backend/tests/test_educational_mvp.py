import io
from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models.models import (
    Organization,
    User,
    Product,
    Supplier,
    SupplierOffer,
    Purchase,
    PurchaseOrder,
    InventoryMovement,
    FinancialTransaction,
    ActivityLog,
)
from backend.security import hash_password, verify_password

client = TestClient(app)


def test_password_hashing_and_verification():
    raw = "SecretPassword123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_rbac_and_user_creation():
    # Login as Org 1 Owner
    login_res = client.post("/api/auth/demo-login?org_id=1")
    assert login_res.status_code == 200
    user_data = login_res.json()
    assert user_data["role"] in ["owner", "Управляющий / Владелец"]

    # Owner can create a manager
    new_user_email = f"manager_{datetime.utcnow().timestamp()}@cafearoma.kz"
    create_res = client.post(
        "/api/settings/users",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Тестовый Менеджер",
            "email": new_user_email,
            "password": "ManagerPass123!",
            "role": "manager",
        },
    )
    assert create_res.status_code in [200, 201]
    created = create_res.json()
    assert created["email"] == new_user_email
    assert created["role"] == "manager"

    # Create employee
    emp_email = f"employee_{datetime.utcnow().timestamp()}@cafearoma.kz"
    client.post(
        "/api/settings/users",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Тестовый Бариста",
            "email": emp_email,
            "password": "BaristaPass123!",
            "role": "employee",
        },
    )

    # Login as employee
    login_emp = client.post(
        "/api/auth/login",
        json={"email": emp_email, "password": "BaristaPass123!"},
    )
    assert login_emp.status_code == 200
    emp_token_id = str(login_emp.json()["id"])

    # Employee tries to update org settings -> 403 Forbidden
    forbidden_res = client.put(
        "/api/settings/organization",
        headers={"X-Organization-Id": "1", "X-User-Id": emp_token_id},
        json={"name": "Hacked Name"},
    )
    assert forbidden_res.status_code == 403


def test_cross_tenant_isolation_protection():
    """Verify that Org 2 cannot read or manipulate Org 1 resources via direct ID."""
    db = SessionLocal()
    try:
        org2_prod = db.query(Product).filter(Product.organization_id == 2).first()
        assert org2_prod is not None

        # Org 1 attempts to fetch Org 2 product
        res = client.get(
            f"/api/products/{org2_prod.id}",
            headers={"X-Organization-Id": "1"},
        )
        assert res.status_code == 404

        # Org 1 attempts to update Org 2 product
        update_res = client.put(
            f"/api/products/{org2_prod.id}",
            headers={"X-Organization-Id": "1"},
            json={"name": "Stolen Coffee", "category": "Кофе", "unit": "кг", "minimum_stock": 5.0},
        )
        assert update_res.status_code == 404

        # Org 1 attempts to delete Org 2 product
        del_res = client.delete(
            f"/api/products/{org2_prod.id}",
            headers={"X-Organization-Id": "1"},
        )
        assert del_res.status_code == 404
    finally:
        db.close()


def test_product_catalog_crud():
    # 1. Create product
    sku_val = f"TEST-SKU-{int(datetime.utcnow().timestamp())}"
    create_res = client.post(
        "/api/products",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Сироп Карамель 1л",
            "sku": sku_val,
            "category": "Сиропы",
            "unit": "бут",
            "current_stock": 10.0,
            "minimum_stock": 3.0,
            "description": "Французский сироп для рафов",
        },
    )
    assert create_res.status_code in [200, 201]
    prod = create_res.json()
    prod_id = prod["id"]
    assert prod["name"] == "Сироп Карамель 1л"
    assert prod["current_stock"] == 10.0

    # 2. Get product
    get_res = client.get(f"/api/products/{prod_id}", headers={"X-Organization-Id": "1"})
    assert get_res.status_code == 200
    assert get_res.json()["sku"] == sku_val

    # 3. Update product
    upd_res = client.put(
        f"/api/products/{prod_id}",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Сироп Соленая Карамель 1л",
            "category": "Сиропы",
            "unit": "бут",
            "minimum_stock": 4.0,
        },
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Сироп Соленая Карамель 1л"
    assert upd_res.json()["minimum_stock"] == 4.0

    # 4. Search and filter
    list_res = client.get(
        "/api/products?category=Сиропы&search=Соленая",
        headers={"X-Organization-Id": "1"},
    )
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1
    assert any(i["id"] == prod_id for i in items)

    # 5. Delete (archive)
    del_res = client.delete(f"/api/products/{prod_id}", headers={"X-Organization-Id": "1"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # After archiving, it shouldn't appear in default active list
    list_after = client.get(
        "/api/products?include_archived=false",
        headers={"X-Organization-Id": "1"},
    ).json()
    assert not any(i["id"] == prod_id for i in list_after)


def test_supplier_and_price_history_crud():
    # 1. Create Supplier
    sup_name = f"Поставщик Упаковки {int(datetime.utcnow().timestamp())}"
    create_sup = client.post(
        "/api/suppliers",
        headers={"X-Organization-Id": "1"},
        json={
            "name": sup_name,
            "contact_name": "Айдар Кунанбаев",
            "phone": "+7 701 555 1234",
            "email": "aidar@upakovka.kz",
            "delivery_cost": 1500.0,
            "minimum_order_amount": 10000.0,
            "address": "г. Астана, ул. Промышленная 12",
        },
    )
    assert create_sup.status_code in [200, 201]
    sup = create_sup.json()
    sup_id = sup["id"]
    assert sup["name"] == sup_name

    # 2. Add product and offer
    prod_res = client.post(
        "/api/products",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Стаканы 300мл Крафт",
            "category": "Упаковка",
            "unit": "уп",
            "current_stock": 5.0,
            "minimum_stock": 10.0,
        },
    )
    assert prod_res.status_code in [200, 201]
    prod_id = prod_res.json()["id"]

    offer_res = client.post(
        f"/api/suppliers/{sup_id}/offers",
        headers={"X-Organization-Id": "1"},
        json={
            "product_id": prod_id,
            "offered_price": 2800.0,
            "unit": "уп",
            "package_quantity": 50.0,
            "minimum_order_quantity": 5.0,
            "delivery_cost": 1500.0,
        },
    )
    assert offer_res.status_code in [200, 201]
    offer = offer_res.json()
    assert offer["offered_price"] == 2800.0

    # 3. Update price and verify OfferPriceHistory
    offer_upd = client.post(
        f"/api/suppliers/{sup_id}/offers",
        headers={"X-Organization-Id": "1"},
        json={
            "product_id": prod_id,
            "offered_price": 3100.0,
            "unit": "уп",
            "package_quantity": 50.0,
            "minimum_order_quantity": 5.0,
            "delivery_cost": 1500.0,
        },
    )
    assert offer_upd.status_code in [200, 201]
    assert offer_upd.json()["offered_price"] == 3100.0

    # Verify price history entry was recorded in DB
    db = SessionLocal()
    try:
        from backend.models.models import OfferPriceHistory
        history = db.query(OfferPriceHistory).filter(
            OfferPriceHistory.supplier_id == sup_id,
            OfferPriceHistory.product_id == prod_id,
        ).all()
        assert len(history) >= 1
        last_change = history[-1]
        assert last_change.old_price == 2800.0
        assert last_change.new_price == 3100.0
    finally:
        db.close()


def test_purchase_order_lifecycle_and_inventory_reception():
    # 1. Create Product & Supplier
    prod_res = client.post(
        "/api/products",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Чай Матча Премиум",
            "category": "Чай",
            "unit": "кг",
            "current_stock": 2.0,
            "minimum_stock": 5.0,
        },
    )
    assert prod_res.status_code in [200, 201]
    prod_id = prod_res.json()["id"]

    sup_res = client.post(
        "/api/suppliers",
        headers={"X-Organization-Id": "1"},
        json={"name": "Matcha Japan Import", "delivery_cost": 2000.0},
    )
    assert sup_res.status_code in [200, 201]
    sup_id = sup_res.json()["id"]

    # 2. Create PurchaseOrder in Draft
    order_create_res = client.post(
        "/api/orders",
        headers={"X-Organization-Id": "1"},
        json={
            "supplier_id": sup_id,
            "order_date": str(date.today()),
            "delivery_cost": 2000.0,
            "notes": "Срочная поставка к фестивалю",
            "items": [
                {
                    "product_id": prod_id,
                    "ordered_quantity": 5.0,
                    "unit": "кг",
                    "unit_price": 12000.0,
                }
            ],
        },
    )
    assert order_create_res.status_code in [200, 201]
    order = order_create_res.json()
    order_id = order["id"]
    assert order["status"] == "draft"
    assert order["subtotal_amount"] == 60000.0
    assert order["total_amount"] == 62000.0

    # 3. Confirm order
    confirm_res = client.put(
        f"/api/orders/{order_id}",
        headers={"X-Organization-Id": "1"},
        json={"status": "confirmed"},
    )
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "confirmed"

    # 4. Generate order document
    doc_res = client.get(f"/api/orders/{order_id}/document", headers={"X-Organization-Id": "1"})
    assert doc_res.status_code == 200
    doc_text = doc_res.text
    assert "БЛАНК ЗАКАЗА НА ЗАКУПКУ" in doc_text
    assert "Matcha Japan Import" in doc_text
    assert "62 000" in doc_text or "62000" in doc_text

    # 5. Receive order (Receipt of goods)
    receive_res = client.post(
        f"/api/orders/{order_id}/receive",
        headers={"X-Organization-Id": "1"},
        json={
            "received_quantities": {order["items"][0]["id"]: 5.0},
            "record_financial_expense": True,
            "payment_method": "cashless",
        },
    )
    assert receive_res.status_code == 200
    received_order = receive_res.json()
    assert received_order["status"] == "received"

    # 6. Verify stock has increased from 2.0 to 7.0
    prod_after = client.get(f"/api/products/{prod_id}", headers={"X-Organization-Id": "1"}).json()
    assert prod_after["current_stock"] == 7.0

    # 7. Verify inventory movement created
    moves_res = client.get(
        f"/api/inventory/movements?product_id={prod_id}",
        headers={"X-Organization-Id": "1"},
    )
    assert moves_res.status_code == 200
    moves = moves_res.json()
    assert len(moves) >= 1
    assert moves[0]["movement_type"] == "receipt"
    assert moves[0]["quantity"] == 5.0
    assert moves[0]["resulting_stock"] == 7.0

    # 8. Verify Financial Transaction created without duplicate
    txs_res = client.get("/api/finances", headers={"X-Organization-Id": "1"}).json()
    order_tx = next((t for t in txs_res if t.get("purchase_order_id") == order_id), None)
    assert order_tx is not None
    assert order_tx["amount"] == 62000.0
    assert order_tx["transaction_type"] == "expense"

    # 9. Verify double receipt prevention
    repeat_receive = client.post(
        f"/api/orders/{order_id}/receive",
        headers={"X-Organization-Id": "1"},
        json={},
    )
    assert repeat_receive.status_code == 400


def test_inventory_adjust_and_write_off():
    # 1. Create Product
    prod_res = client.post(
        "/api/products",
        headers={"X-Organization-Id": "1"},
        json={"name": "Сироп Ваниль 1л", "category": "Сиропы", "unit": "бут", "current_stock": 10.0, "minimum_stock": 2.0},
    )
    assert prod_res.status_code in [200, 201]
    prod_id = prod_res.json()["id"]

    # 2. Write-off (spoilage of 2 bottles)
    writeoff_res = client.post(
        "/api/inventory/write-off",
        headers={"X-Organization-Id": "1"},
        json={"product_id": prod_id, "quantity": 2.0, "reason": "Разбита при транспортировке"},
    )
    assert writeoff_res.status_code == 200
    move = writeoff_res.json()
    assert move["movement_type"] == "write_off"
    assert move["quantity"] == -2.0
    assert move["resulting_stock"] == 8.0

    # Verify stock updated
    p_check = client.get(f"/api/products/{prod_id}", headers={"X-Organization-Id": "1"}).json()
    assert p_check["current_stock"] == 8.0

    # 3. Stock adjustment (audit count finds 9 bottles)
    adjust_res = client.post(
        "/api/inventory/adjust",
        headers={"X-Organization-Id": "1"},
        json={"product_id": prod_id, "actual_stock": 9.0, "reason": "Плановая инвентаризация бара"},
    )
    assert adjust_res.status_code == 200
    adj_move = adjust_res.json()
    assert adj_move["movement_type"] == "adjustment"
    assert adj_move["quantity"] == 1.0  # +1 diff
    assert adj_move["resulting_stock"] == 9.0

    # 4. Export inventory test
    export_xlsx = client.get("/api/inventory/export?format=xlsx", headers={"X-Organization-Id": "1"})
    assert export_xlsx.status_code == 200
    assert export_xlsx.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(export_xlsx.content) > 100


def test_finances_crud_and_summary():
    # 1. Create Transaction
    t_date = str(date.today())
    create_tx = client.post(
        "/api/finances",
        headers={"X-Organization-Id": "1"},
        json={
            "transaction_date": t_date,
            "description": "Оплата интернет-провайдеру Kazakhtelecom",
            "category": "Коммунальные услуги",
            "amount": 15000.0,
            "transaction_type": "expense",
            "payment_method": "cashless",
        },
    )
    assert create_tx.status_code in [200, 201]
    tx = create_tx.json()
    tx_id = tx["id"]
    assert tx["amount"] == 15000.0

    # 2. Summary
    sum_res = client.get("/api/finances/summary", headers={"X-Organization-Id": "1"})
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["total_expenses"] > 0

    # 3. Update Transaction
    upd_res = client.put(
        f"/api/finances/{tx_id}",
        headers={"X-Organization-Id": "1"},
        json={"amount": 16500.0, "description": "Оплата интернет + статический IP"},
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["amount"] == 16500.0

    # 4. Delete Transaction (soft archive)
    del_res = client.delete(f"/api/finances/{tx_id}", headers={"X-Organization-Id": "1"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # 5. Export finances
    exp_csv = client.get("/api/finances/export?format=csv", headers={"X-Organization-Id": "1"})
    assert exp_csv.status_code == 200
    assert "text/csv" in exp_csv.headers["content-type"]
    assert len(exp_csv.content) > 50


def test_price_comparison_and_staleness_warning():
    # Product with an offer > 30 days old
    db = SessionLocal()
    try:
        prod = Product(organization_id=1, name="Сахар порционный 5г", category="Бакалея", unit="уп", current_stock=20.0, minimum_stock=5.0)
        sup1 = Supplier(organization_id=1, name="СахарОпт", delivery_cost=500.0)
        sup2 = Supplier(organization_id=1, name="БакалеяСбыт", delivery_cost=1000.0)
        db.add_all([prod, sup1, sup2])
        db.flush()

        # Current purchase from sup1
        p = Purchase(
            organization_id=1,
            product_id=prod.id,
            supplier_id=sup1.id,
            purchase_date=date.today() - timedelta(days=5),
            quantity=10.0,
            unit="уп",
            unit_price=1500.0,
            total_price=15000.0,
        )
        # Offer from sup2 that is 45 days old (stale)
        o = SupplierOffer(
            organization_id=1,
            product_id=prod.id,
            supplier_id=sup2.id,
            offered_price=1200.0,
            unit="уп",
            package_quantity=1.0,
            minimum_order_quantity=5.0,
            delivery_cost=1000.0,
            updated_at=datetime.utcnow() - timedelta(days=45),
            is_active=True,
        )
        db.add_all([p, o])
        db.commit()
        prod_id = prod.id
    finally:
        db.close()

    comp_res = client.get(f"/api/purchases/comparison/{prod_id}?quantity=10", headers={"X-Organization-Id": "1"})
    assert comp_res.status_code == 200
    comp = comp_res.json()
    assert comp["current_unit_price"] == 1500.0
    assert len(comp["alternative_offers"]) == 1
    alt = comp["alternative_offers"][0]
    assert alt["is_stale"] is True
    assert "30 дней" in alt["warning_note"]


def test_forecast_insufficient_data_handling():
    # Product with no history
    prod_res = client.post(
        "/api/products",
        headers={"X-Organization-Id": "1"},
        json={"name": "Новый Экзотический Сироп", "category": "Сиропы", "unit": "бут", "current_stock": 5.0, "minimum_stock": 2.0},
    )
    assert prod_res.status_code in [200, 201]
    prod_id = prod_res.json()["id"]

    fore_res = client.get("/api/forecast", headers={"X-Organization-Id": "1"}).json()
    item = next(i for i in fore_res["items"] if i["product_id"] == prod_id)
    assert item["status"] == "insufficient_data"
    assert item["avg_daily_consumption"] == 0.0
    assert item["days_left"] is None
    assert "Недостаточно данных" in item["calculation_method"]


def test_excel_templates_and_import_error_handling():
    # 1. Download template
    tmpl_res = client.get("/api/import/templates/finances")
    assert tmpl_res.status_code == 200
    assert len(tmpl_res.content) > 100

    # 2. Preview valid CSV
    uniq_desc = f"Тестовый доход {int(datetime.utcnow().timestamp())}"
    csv_data = f"Дата,Описание,Сумма,Тип,Категория\n2026-10-20,{uniq_desc},50000,Доход,Выручка / Продажи\n"
    preview_res = client.post(
        "/api/import/preview",
        files={"file": ("test.csv", csv_data.encode("utf-8"), "text/csv")},
        data={"import_type": "finances"},
    )
    assert preview_res.status_code == 200
    assert preview_res.json()["is_valid"] is True
    assert preview_res.json()["total_rows"] == 1

    # 3. Preview invalid file missing required columns
    bad_csv = "Колонка1,Колонка2\n123,456\n"
    bad_preview = client.post(
        "/api/import/preview",
        files={"file": ("bad.csv", bad_csv.encode("utf-8"), "text/csv")},
        data={"import_type": "finances"},
    )
    assert bad_preview.status_code == 200
    assert bad_preview.json()["is_valid"] is False
    assert "Не найдены обязательные колонки" in bad_preview.json()["message"]

    # 4. Execute valid import
    exec_res = client.post(
        "/api/import/execute",
        headers={"X-Organization-Id": "1"},
        files={"file": ("test_exec.csv", csv_data.encode("utf-8"), "text/csv")},
        data={"import_type": "finances"},
    )
    assert exec_res.status_code == 200
    res_data = exec_res.json()
    assert res_data["rows_imported"] == 1
    assert res_data["status"] == "success"

    # 5. Re-executing same file should deduplicate (skip)
    exec_res2 = client.post(
        "/api/import/execute",
        headers={"X-Organization-Id": "1"},
        files={"file": ("test_exec.csv", csv_data.encode("utf-8"), "text/csv")},
        data={"import_type": "finances"},
    )
    assert exec_res2.status_code == 200
    assert exec_res2.json()["rows_skipped"] == 1
    assert exec_res2.json()["rows_imported"] == 0

