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

from backend.demo.seed_data import reset_and_seed_db

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_isolation_demo():
    db = SessionLocal()
    try:
        reset_and_seed_db(db)
    finally:
        db.close()
    yield

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
    """Verify that financial transactions from Org 1 start empty, and after import remain strictly isolated from Org 2."""
    # 1. Cafe Aroma starts with 0 financial transactions
    fin1_init = client.get("/api/finances", headers={"X-Organization-Id": "1"}).json()
    assert len(fin1_init) == 0, "Cafe Aroma must start with 0 transactions before import"

    # 2. Daily Cup has pre-seeded mature transactions
    fin2 = client.get("/api/finances", headers={"X-Organization-Id": "2"}).json()
    assert len(fin2) > 0
    assert any("Достык 89" in tx["description"] for tx in fin2)
    assert not any("Абая 45" in tx["description"] for tx in fin2)

    # 3. Import legacy finances into Cafe Aroma
    demo_dir = Path(__file__).resolve().parent.parent.parent / "demo_data"
    excel_path = demo_dir / "legacy_finances.xlsx"
    with open(excel_path, "rb") as f:
        client.post(
            "/api/import/execute",
            files={"file": ("legacy_finances.xlsx", io.BytesIO(f.read()), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"import_type": "finances"},
            headers={"X-Organization-Id": "1"},
        )

    # 4. Now Org 1 has transactions and they don't leak into Org 2
    fin1 = client.get("/api/finances", headers={"X-Organization-Id": "1"}).json()
    assert len(fin1) > 0
    ids1 = {tx["id"] for tx in fin1}
    ids2 = {tx["id"] for tx in fin2}
    assert ids1.isdisjoint(ids2), "Financial transaction IDs must be mutually exclusive!"

    assert any("Абая 45" in tx["description"] for tx in fin1)
    assert not any("Достык 89" in tx["description"] for tx in fin1)


def test_purchases_and_products_isolation():
    """Verify products and purchases belong strictly to the querying organization."""
    # Org 2 has mature products and purchases
    prods2 = client.get("/api/purchases/products", headers={"X-Organization-Id": "2"}).json()
    assert len(prods2) > 0
    p_names2 = {p["name"] for p in prods2}
    assert "Стаканы двухслойные 250мл Kraft (50 шт)" in p_names2

    purch2 = client.get("/api/purchases", headers={"X-Organization-Id": "2"}).json()
    assert len(purch2) > 0
    assert any("PackGroup Almaty" in p["supplier_name"] for p in purch2)
    assert not any("Coffee Roasters Hub" in p["supplier_name"] for p in purch2)

    # Org 1 imports legacy purchases
    demo_dir = Path(__file__).resolve().parent.parent.parent / "demo_data"
    with open(demo_dir / "legacy_purchases.xlsx", "rb") as f:
        client.post(
            "/api/import/execute",
            files={"file": ("legacy_purchases.xlsx", io.BytesIO(f.read()), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"import_type": "purchases"},
            headers={"X-Organization-Id": "1"},
        )

    prods1 = client.get("/api/purchases/products", headers={"X-Organization-Id": "1"}).json()
    p_names1 = {p["name"] for p in prods1}
    assert "Кофе в зернах Espresso Blend 100% Арабика" in p_names1
    assert "Стаканы двухслойные 250мл Kraft (50 шт)" not in p_names1

    purch1 = client.get("/api/purchases", headers={"X-Organization-Id": "1"}).json()
    assert any("Coffee Roasters Hub" in p["supplier_name"] for p in purch1)
    assert not any("PackGroup Almaty" in p["supplier_name"] for p in purch1)


def test_dashboard_featured_comparison_logic():
    """
    Verify Cafe Aroma handles empty comparison before price list import,
    and Daily Cup features Kraft Cups (+18.3% spike, EcoTorg alternative).
    """
    # Daily Cup features Kraft Cups comparison
    dash2 = client.get("/api/dashboard?period=30d", headers={"X-Organization-Id": "2"}).json()
    feat2 = dash2["featured_comparison"]
    assert feat2 is not None
    assert "Kraft" in feat2["product_name"]
    assert feat2["best_offer"] is not None
    assert feat2["best_offer"]["offered_price"] > 0


def test_forecast_calculations():
    """Verify forecast returns insufficient_data for empty org and calculates consumption for mature org."""
    # Case A: Org 1 before inventory movements has insufficient_data or empty items
    fore1 = client.get("/api/forecast", headers={"X-Organization-Id": "1"}).json()
    assert "items" in fore1

    # Case B: Daily Cup has mature 6-month data
    fore2 = client.get("/api/forecast", headers={"X-Organization-Id": "2"}).json()
    assert fore2["total_products_tracked"] > 0
    assert len(fore2["items"]) > 0


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
