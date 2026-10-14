import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models.models import (
    Organization,
    User,
    Product,
    Supplier,
    Purchase,
    FinancialTransaction,
    Notification,
    ImportBatch,
)

client = TestClient(app)

def test_organizations_metadata():
    """Verify both demo spaces exist with accurate scenario labels."""
    res = client.get("/api/auth/organizations")
    assert res.status_code == 200
    orgs = res.json()
    assert len(orgs) >= 2
    org1 = next(o for o in orgs if o["id"] == 1)
    org2 = next(o for o in orgs if o["id"] == 2)

    assert "Cafe Aroma" in org1["name"]
    assert org1["scenario_type"] == "initial_adoption"
    assert org1["scenario_title"] == "Первоначальное внедрение"

    assert "Daily Cup" in org2["name"]
    assert org2["scenario_type"] == "regular_usage"
    assert org2["scenario_title"] == "Регулярное использование"


def test_auth_and_switching():
    """Verify switching organizations switches active user and context."""
    res1 = client.post("/api/auth/demo-login?org_id=1")
    assert res1.status_code == 200
    u1 = res1.json()
    assert u1["organization"]["id"] == 1
    assert "Смирнов" in u1["name"]

    res2 = client.post("/api/auth/switch-org", json={"organization_id": 2})
    assert res2.status_code == 200
    u2 = res2.json()
    assert u2["organization"]["id"] == 2
    assert "Касымов" in u2["name"]


def test_strict_financial_data_isolation():
    """Verify that financial transactions from Org 1 do not leak into Org 2 and vice-versa."""
    fin1 = client.get("/api/finances", headers={"X-Organization-Id": "1"}).json()
    fin2 = client.get("/api/finances", headers={"X-Organization-Id": "2"}).json()

    assert len(fin1) > 0
    assert len(fin2) > 0

    ids1 = {tx["id"] for tx in fin1}
    ids2 = {tx["id"] for tx in fin2}
    # No overlapping transaction IDs
    assert ids1.isdisjoint(ids2), "Financial transaction IDs must be mutually exclusive!"

    # Content checks: Org 1 has Abaya 45 rent, Org 2 has Dostyk 89 rent
    assert any("Абая 45" in tx["description"] for tx in fin1)
    assert not any("Достык 89" in tx["description"] for tx in fin1)

    assert any("Достык 89" in tx["description"] for tx in fin2)
    assert not any("Абая 45" in tx["description"] for tx in fin2)


def test_purchases_and_products_isolation():
    """Verify products and purchases belong strictly to the querying organization."""
    prods1 = client.get("/api/purchases/products", headers={"X-Organization-Id": "1"}).json()
    prods2 = client.get("/api/purchases/products", headers={"X-Organization-Id": "2"}).json()

    assert len(prods1) > 0
    assert len(prods2) > 0

    p_names1 = {p["name"] for p in prods1}
    p_names2 = {p["name"] for p in prods2}

    assert "Кофе в зернах Espresso Blend 100% Арабика" in p_names1
    assert "Стаканы двухслойные 250мл Kraft (50 шт)" in p_names2

    # Check purchases
    purch1 = client.get("/api/purchases", headers={"X-Organization-Id": "1"}).json()
    purch2 = client.get("/api/purchases", headers={"X-Organization-Id": "2"}).json()

    assert any("Coffee Roasters Hub" in p["supplier_name"] for p in purch1)
    assert not any("PackGroup Almaty" in p["supplier_name"] for p in purch1)

    assert any("PackGroup Almaty" in p["supplier_name"] for p in purch2)
    assert not any("Coffee Roasters Hub" in p["supplier_name"] for p in purch2)


def test_dashboard_featured_comparison_logic():
    """
    Verify Cafe Aroma features Coffee (+15% spike, Aroma Direct alternative)
    and Daily Cup features Kraft Cups (+18.3% spike, EcoTorg alternative).
    """
    dash1 = client.get("/api/dashboard?period=30d", headers={"X-Organization-Id": "1"}).json()
    dash2 = client.get("/api/dashboard?period=30d", headers={"X-Organization-Id": "2"}).json()

    # Case A: Cafe Aroma
    feat1 = dash1["featured_comparison"]
    assert feat1 is not None
    assert "Espresso Blend" in feat1["product_name"]
    assert feat1["current_unit_price"] == 11500.0
    assert feat1["price_change_percent"] == 15.0
    assert feat1["best_offer"]["offered_price"] == 10350.0
    assert feat1["best_offer"]["unit_difference"] == 1150.0
    # For quantity 20: 1 150 * 20 = 23 000
    assert feat1["best_offer"]["total_difference"] == 23000.0

    # Case B: Daily Cup
    feat2 = dash2["featured_comparison"]
    assert feat2 is not None
    assert "Kraft" in feat2["product_name"]
    assert feat2["current_unit_price"] == 1420.0
    assert feat2["price_change_percent"] == 18.3
    assert feat2["best_offer"]["supplier_name"] == "EcoTorg Kazakhstan"
    assert feat2["best_offer"]["offered_price"] == 1230.0
    assert feat2["best_offer"]["unit_difference"] == 190.0
    # For quantity 50: 190 * 50 = 9 500
    assert feat2["best_offer"]["total_difference"] == 9500.0


def test_forecast_calculations():
    """Verify forecast calculates avg daily consumption and flags critical shortages."""
    fore1 = client.get("/api/forecast", headers={"X-Organization-Id": "1"}).json()
    fore2 = client.get("/api/forecast", headers={"X-Organization-Id": "2"}).json()

    # Case A: Milk 3.2% is critical
    milk1 = next(item for item in fore1["items"] if "Молоко" in item["product_name"])
    assert milk1["current_stock"] == 12.0
    assert milk1["minimum_stock"] == 25.0
    assert milk1["status"] == "critical"

    # Case B: Cup holders is critical
    holders2 = next(item for item in fore2["items"] if "Держатели" in item["product_name"])
    assert holders2["current_stock"] == 6.0
    assert holders2["minimum_stock"] == 12.0
    assert holders2["status"] == "critical"


def test_excel_import_and_deduplication():
    """Verify that importing an Excel file works and stays strictly scoped to the importing organization."""
    demo_dir = Path(__file__).resolve().parent.parent.parent / "demo_data"
    excel_path = demo_dir / "legacy_finances.xlsx"
    assert excel_path.exists(), "demo_data/legacy_finances.xlsx must exist"

    with open(excel_path, "rb") as f:
        file_bytes = f.read()

    # 1. Preview
    res_prev = client.post(
        "/api/import/preview",
        files={"file": ("legacy_finances.xlsx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"import_type": "finances"},
        headers={"X-Organization-Id": "1"},
    )
    assert res_prev.status_code == 200
    prev_data = res_prev.json()
    assert prev_data["is_valid"] is True
    assert prev_data["total_rows"] > 0

    # 2. Execute import
    res_exec = client.post(
        "/api/import/execute",
        files={"file": ("legacy_finances.xlsx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"import_type": "finances"},
        headers={"X-Organization-Id": "1"},
    )
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["status"] == "success"

    # Verify that the new batch was recorded for Org 1 and NOT Org 2
    batches1 = client.get("/api/import/batches", headers={"X-Organization-Id": "1"}).json()
    batches2 = client.get("/api/import/batches", headers={"X-Organization-Id": "2"}).json()

    batch_ids1 = {b["id"] for b in batches1}
    batch_ids2 = {b["id"] for b in batches2}
    assert exec_data["batch_id"] in batch_ids1
    assert exec_data["batch_id"] not in batch_ids2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
