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
