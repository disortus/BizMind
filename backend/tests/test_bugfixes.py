import pytest
from datetime import date
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_inventory_and_finances_excel_export_alias():
    """Verify that export?format=excel works without 422 error for both inventory and finances."""
    # Inventory excel export
    res_inv = client.get("/api/inventory/export?format=excel", headers={"X-Organization-Id": "2"})
    assert res_inv.status_code == 200
    assert "spreadsheetml" in res_inv.headers.get("content-type", "")

    # Finances excel export
    res_fin = client.get("/api/finances/export?format=excel", headers={"X-Organization-Id": "2"})
    assert res_fin.status_code == 200
    assert "spreadsheetml" in res_fin.headers.get("content-type", "")


def test_settings_activity_endpoint_alias_and_initial_logs():
    """Verify /settings/activity and /settings/activity-logs both return 200 and logs exist."""
    res_act = client.get("/api/settings/activity", headers={"X-Organization-Id": "2"})
    assert res_act.status_code == 200
    logs_act = res_act.json()
    assert isinstance(logs_act, list)
    assert len(logs_act) > 0, "Daily Cup should have pre-seeded activity logs"

    res_logs = client.get("/api/settings/activity-logs", headers={"X-Organization-Id": "2"})
    assert res_logs.status_code == 200
    assert len(res_logs.json()) == len(logs_act)

    # Cafe Aroma also has activity logs
    res_aroma = client.get("/api/settings/activity", headers={"X-Organization-Id": "1"})
    assert res_aroma.status_code == 200
    assert len(res_aroma.json()) > 0, "Cafe Aroma should have initial initialization activity log"


def test_settings_users_list_populated():
    """Verify that users are returned for both organizations."""
    res_users1 = client.get("/api/settings/users", headers={"X-Organization-Id": "1"})
    assert res_users1.status_code == 200
    users1 = res_users1.json()
    assert len(users1) >= 2, "Cafe Aroma should have owner and staff users"

    res_users2 = client.get("/api/settings/users", headers={"X-Organization-Id": "2"})
    assert res_users2.status_code == 200
    users2 = res_users2.json()
    assert len(users2) >= 3, "Daily Cup should have team members"


def test_organization_settings_alias_and_validation():
    """Verify settings update accepts price_alert_threshold_percent and rejects invalid data."""
    # Valid update with frontend alias
    res_up = client.put(
        "/api/settings/organization",
        headers={"X-Organization-Id": "1"},
        json={
            "name": "Кофейня «Cafe Aroma»",
            "price_alert_threshold_percent": 7.5,
            "contact_email": "hello@cafearoma.kz",
        },
    )
    assert res_up.status_code == 200
    data = res_up.json()
    assert data["alert_threshold_percent"] == 7.5
    assert data["price_alert_threshold_percent"] == 7.5
    assert data["email"] == "hello@cafearoma.kz"
    assert data["contact_email"] == "hello@cafearoma.kz"

    # Validation rejection for negative or out-of-range threshold
    res_invalid = client.put(
        "/api/settings/organization",
        headers={"X-Organization-Id": "1"},
        json={"price_alert_threshold_percent": 150.0},
    )
    assert res_invalid.status_code == 422

    # Validation rejection for invalid email
    res_invalid_email = client.put(
        "/api/settings/organization",
        headers={"X-Organization-Id": "1"},
        json={"contact_email": "not-an-email"},
    )
    assert res_invalid_email.status_code == 422


def test_purchase_order_item_quantity_alias_and_creation():
    """Verify purchase order creation accepts 'quantity' in items without 422 error."""
    # Get products for org 2
    res_prods = client.get("/api/products", headers={"X-Organization-Id": "2"})
    assert res_prods.status_code == 200
    prods = res_prods.json()
    assert len(prods) > 0
    target_prod = prods[0]

    # Get suppliers for org 2
    res_sups = client.get("/api/suppliers", headers={"X-Organization-Id": "2"})
    assert res_sups.status_code == 200
    sups = res_sups.json()
    assert len(sups) > 0
    target_sup = sups[0]

    order_payload = {
        "supplier_id": target_sup["id"],
        "order_date": date.today().isoformat(),
        "delivery_cost": 500.0,
        "notes": "Тестовый заказ для проверки алиаса quantity",
        "items": [
            {
                "product_id": target_prod["id"],
                "quantity": 15.0,  # sending quantity instead of ordered_quantity!
                "unit_price": 1200.0,
            }
        ],
    }

    res_order = client.post("/api/orders", headers={"X-Organization-Id": "2"}, json=order_payload)
    assert res_order.status_code == 201
    created_order = res_order.json()
    assert created_order["total_amount"] == 15.0 * 1200.0 + 500.0
    assert len(created_order["items"]) == 1
    assert created_order["items"][0]["ordered_quantity"] == 15.0


def test_order_creation_default_date_and_confirm_cancel():
    """Verify purchase order creation without order_date defaults to today and confirm/cancel endpoints work."""
    res_sups = client.get("/api/suppliers", headers={"X-Organization-Id": "2"})
    sups = res_sups.json()
    res_prods = client.get("/api/products", headers={"X-Organization-Id": "2"})
    prods = res_prods.json()

    # Omit order_date from payload
    order_payload = {
        "supplier_id": sups[0]["id"],
        "delivery_cost": 0.0,
        "items": [
            {
                "product_id": prods[0]["id"],
                "quantity": 5.0,
                "unit_price": 2000.0,
            }
        ],
    }

    res_create = client.post("/api/orders", headers={"X-Organization-Id": "2"}, json=order_payload)
    assert res_create.status_code == 201
    order = res_create.json()
    assert order["order_date"] == date.today().isoformat()
    assert order["status"] == "draft"

    # Confirm order via POST /orders/{id}/confirm
    res_conf = client.post(f"/api/orders/{order['id']}/confirm", headers={"X-Organization-Id": "2"})
    assert res_conf.status_code == 200
    assert res_conf.json()["status"] == "confirmed"

    # Create another order to test cancel
    res_create2 = client.post("/api/orders", headers={"X-Organization-Id": "2"}, json=order_payload)
    order2 = res_create2.json()
    res_canc = client.post(f"/api/orders/{order2['id']}/cancel", headers={"X-Organization-Id": "2"})
    assert res_canc.status_code == 200
    assert res_canc.json()["status"] == "cancelled"


def test_supplier_catalog_and_moq_and_draft_editing():
    """Verify supplier catalog endpoint, minimum order validation, and draft order item updates."""
    # 1. Supplier catalog endpoint
    cat_res = client.get("/api/suppliers/101/catalog", headers={"X-Organization-Id": "2"})
    assert cat_res.status_code == 200
    catalog = cat_res.json()
    assert len(catalog) > 0
    item = catalog[0]
    assert "product_id" in item
    assert "product_name" in item
    assert "unit_price" in item
    assert item["unit_price"] > 0

    # 2. Minimum order amount validation
    # PackGroup Almaty (id=101) has minimum_order_amount = 20000.0
    sup101 = client.get("/api/suppliers/101", headers={"X-Organization-Id": "2"}).json()
    assert sup101["minimum_order_amount"] == 20000.0

    # Try order below minimum (e.g. 1 unit at 1420 ₸ = 1420 ₸ < 20000 ₸)
    invalid_order = client.post(
        "/api/orders",
        headers={"X-Organization-Id": "2"},
        json={
            "supplier_id": 101,
            "items": [{"product_id": item["product_id"], "ordered_quantity": 1.0, "unit_price": item["unit_price"]}],
        },
    )
    assert invalid_order.status_code == 400
    assert "меньше минимальной суммы закупки" in invalid_order.json()["detail"]

    # Valid order meeting minimum order amount (20 units * 1420 = 28400 >= 20000)
    valid_order_res = client.post(
        "/api/orders",
        headers={"X-Organization-Id": "2"},
        json={
            "supplier_id": 101,
            "delivery_cost": 1500.0,
            "notes": "Начальный черновик",
            "items": [{"product_id": item["product_id"], "ordered_quantity": 20.0, "unit_price": 1420.0}],
        },
    )
    assert valid_order_res.status_code in [200, 201]
    order_data = valid_order_res.json()
    assert order_data["status"] == "draft"
    assert order_data["subtotal_amount"] == 28400.0
    assert order_data["total_amount"] == 29900.0

    # 3. Edit draft order (modify items, quantities, notes)
    order_id = order_data["id"]
    update_res = client.put(
        f"/api/orders/{order_id}",
        headers={"X-Organization-Id": "2"},
        json={
            "notes": "Обновленный черновик",
            "delivery_cost": 1500.0,
            "items": [{"product_id": item["product_id"], "ordered_quantity": 25.0, "unit_price": 1420.0}],
        },
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["notes"] == "Обновленный черновик"
    assert updated["subtotal_amount"] == 35500.0
    assert updated["total_amount"] == 37000.0

    # 4. Confirm order, then verify items cannot be modified anymore
    client.post(f"/api/orders/{order_id}/confirm", headers={"X-Organization-Id": "2"})
    forbidden_edit = client.put(
        f"/api/orders/{order_id}",
        headers={"X-Organization-Id": "2"},
        json={
            "items": [{"product_id": item["product_id"], "ordered_quantity": 30.0, "unit_price": 1420.0}],
        },
    )
    assert forbidden_edit.status_code == 400
    assert "только для заказов в статусе «Черновик»" in forbidden_edit.json()["detail"]
