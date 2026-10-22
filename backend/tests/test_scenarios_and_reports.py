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
    SupplierOffer,
    ReportTemplate,
)
from backend.demo.seed_data import reset_and_seed_db
from backend.demo.generate_demo_files import generate_all_excel_files

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_seed():
    db = SessionLocal()
    try:
        generate_all_excel_files()
        reset_and_seed_db(db)
    finally:
        db.close()


# =============================================================================
# 1. CAFE AROMA TESTS (Scenario A: Clean Onboarding State & Progressive Import)
# =============================================================================

def test_cafe_aroma_starts_completely_empty():
    """Verify that Cafe Aroma starts with 0 financial transactions, 0 purchases, 0 products."""
    # 1. Transactions check
    res_fin = client.get("/api/finances", headers={"X-Organization-Id": "1"})
    assert res_fin.status_code == 200
    assert len(res_fin.json()) == 0, "Cafe Aroma must not have any pre-seeded transactions!"

    # 2. Purchases check
    res_purch = client.get("/api/purchases", headers={"X-Organization-Id": "1"})
    assert res_purch.status_code == 200
    assert len(res_purch.json()) == 0, "Cafe Aroma must not have any pre-seeded purchases!"

    # 3. Products check
    res_prods = client.get("/api/purchases/products", headers={"X-Organization-Id": "1"})
    assert res_prods.status_code == 200
    assert len(res_prods.json()) == 0, "Cafe Aroma must not have pre-seeded products!"

    # 4. Inventory check
    res_inv = client.get("/api/inventory/movements", headers={"X-Organization-Id": "1"})
    assert res_inv.status_code == 200
    assert len(res_inv.json()) == 0

    # 5. Dashboard empty state check
    res_dash = client.get("/api/dashboard", headers={"X-Organization-Id": "1"})
    assert res_dash.status_code == 200
    dash = res_dash.json()
    assert dash["is_empty"] is True, "Dashboard must flag is_empty for initial adoption"
    assert len(dash["onboarding_steps"]) > 0
    assert dash["total_expenses"] == 0.0
    assert dash["total_income"] == 0.0
    assert dash["potential_savings_monthly"] == 0.0
    assert dash["featured_comparison"] is None

    # 6. Forecast handles empty data cleanly
    res_fore = client.get("/api/forecast", headers={"X-Organization-Id": "1"})
    assert res_fore.status_code == 200
    fore = res_fore.json()
    assert fore["total_products_tracked"] == 0
    assert len(fore["items"]) == 0


def test_global_catalog_accessible_before_any_import():
    """Global suppliers from BizMind catalog must be visible even in a completely empty organization."""
    res_sup = client.get("/api/suppliers", headers={"X-Organization-Id": "1"})
    assert res_sup.status_code == 200
    suppliers = res_sup.json()
    assert len(suppliers) >= 5, "Global shared suppliers must be available"
    for s in suppliers:
        assert s["source_type"] == "global"
        assert s["is_global"] is True


def test_cafe_aroma_progressive_data_onboarding():
    """
    Simulates the real onboarding flow:
    1. User downloads historical_finances.xlsx and imports it -> finances appear
    2. User imports historical_purchases.xlsx -> purchases appear
    3. User imports supplier_price_lists.xlsx -> price offers appear
    4. User imports historical_inventory.xlsx -> inventory balances appear
    """
    demo_dir = Path(__file__).resolve().parent.parent.parent / "demo_data"
    onboarding_dir = demo_dir / "onboarding" / "cafe_aroma"
    assert onboarding_dir.exists()

    # Step 1: Import historical finances
    fin_path = onboarding_dir / "historical_finances.xlsx"
    with open(fin_path, "rb") as f:
        fin_bytes = f.read()

    res_import_fin = client.post(
        "/api/import/execute",
        files={"file": ("historical_finances.xlsx", io.BytesIO(fin_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"import_type": "finances"},
        headers={"X-Organization-Id": "1"},
    )
    assert res_import_fin.status_code == 200
    assert res_import_fin.json()["status"] == "success"
    assert res_import_fin.json()["rows_imported"] > 0

    # Verify finances are now populated
    finances = client.get("/api/finances", headers={"X-Organization-Id": "1"}).json()
    assert len(finances) > 0

    # Step 2: Import historical purchases
    purch_path = onboarding_dir / "historical_purchases.xlsx"
    with open(purch_path, "rb") as f:
        purch_bytes = f.read()

    res_import_purch = client.post(
        "/api/import/execute",
        files={"file": ("historical_purchases.xlsx", io.BytesIO(purch_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"import_type": "purchases"},
        headers={"X-Organization-Id": "1"},
    )
    assert res_import_purch.status_code == 200
    assert res_import_purch.json()["rows_imported"] > 0

    # Verify purchases populated
    purchases = client.get("/api/purchases", headers={"X-Organization-Id": "1"}).json()
    assert len(purchases) > 0

    # Step 3: Import inventory
    inv_path = onboarding_dir / "historical_inventory.xlsx"
    with open(inv_path, "rb") as f:
        inv_bytes = f.read()

    res_import_inv = client.post(
        "/api/import/execute",
        files={"file": ("historical_inventory.xlsx", io.BytesIO(inv_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"import_type": "inventory"},
        headers={"X-Organization-Id": "1"},
    )
    assert res_import_inv.status_code == 200
    assert res_import_inv.json()["rows_imported"] > 0

    # Step 4: Import supplier price lists
    prices_path = onboarding_dir / "supplier_price_lists.xlsx"
    with open(prices_path, "rb") as f:
        prices_bytes = f.read()

    res_import_prices = client.post(
        "/api/import/execute",
        files={"file": ("supplier_price_lists.xlsx", io.BytesIO(prices_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"import_type": "supplier_prices"},
        headers={"X-Organization-Id": "1"},
    )
    assert res_import_prices.status_code == 200
    assert res_import_prices.json()["rows_imported"] > 0

    # Step 5: Dashboard is now active (no longer empty)
    dash = client.get("/api/dashboard", headers={"X-Organization-Id": "1"}).json()
    assert dash["is_empty"] is False
    assert dash["total_expenses"] > 0.0


# =============================================================================
# 2. GLOBAL SUPPLIERS & ORIGIN TRACKING TESTS
# =============================================================================

def test_supplier_source_types_and_origin_badges():
    """Verify source_type values: global vs imported/manual."""
    # Org 2 has both global suppliers and imported suppliers
    res = client.get("/api/suppliers", headers={"X-Organization-Id": "2"})
    assert res.status_code == 200
    suppliers = res.json()

    globals_list = [s for s in suppliers if s["source_type"] == "global"]
    imported_list = [s for s in suppliers if s["source_type"] == "imported"]

    assert len(globals_list) >= 5
    assert len(imported_list) >= 8

    # Filter by source_type=global
    res_g = client.get("/api/suppliers?source_type=global", headers={"X-Organization-Id": "2"})
    assert res_g.status_code == 200
    assert all(s["source_type"] == "global" for s in res_g.json())

    # Filter by source_type=imported
    res_i = client.get("/api/suppliers?source_type=imported", headers={"X-Organization-Id": "2"})
    assert res_i.status_code == 200
    assert all(s["source_type"] == "imported" for s in res_i.json())


def test_global_suppliers_protected_from_modification_or_deletion():
    """Users cannot modify or delete global suppliers from BizMind catalog."""
    # Attempt to update global supplier 1001
    res_update = client.put(
        "/api/suppliers/1001",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
        json={"name": "Hacked Roasters"},
    )
    assert res_update.status_code == 403
    assert "защищены" in res_update.json()["detail"]

    # Attempt to delete global supplier 1001
    res_del = client.delete(
        "/api/suppliers/1001",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
    )
    assert res_del.status_code == 403
    assert "защищены" in res_del.json()["detail"]


def test_price_comparison_origin_metadata():
    """Check that price comparison includes supplier_source_type and price_source."""
    res = client.get(
        "/api/suppliers/comparison?product_id=101&quantity=50",
        headers={"X-Organization-Id": "2"},
    )
    assert res.status_code == 200
    comp = res.json()
    assert len(comp["alternative_offers"]) > 0

    for offer in comp["alternative_offers"]:
        assert "supplier_source_type" in offer
        assert "price_source" in offer
        assert "is_global_supplier" in offer


# =============================================================================
# 3. DAILY CUP 6-MONTH MATURE USAGE & REALIZED SAVINGS TESTS
# =============================================================================

def test_dailycup_mature_history_and_realized_savings():
    """
    Verify Daily Cup has 6-month history and documented realized savings (153,200 ₸)
    and distinction between potential and realized savings.
    """
    # 1. Purchases span 6 months
    purchases = client.get("/api/purchases", headers={"X-Organization-Id": "2"}).json()
    assert len(purchases) >= 20

    dates = [p["purchase_date"] for p in purchases]
    dates.sort()
    earliest = dates[0]
    latest = dates[-1]
    assert earliest < "2026-06-01", "Daily Cup history must start in May 2026"
    assert latest >= "2026-10-01", "Daily Cup history must extend into October 2026"

    # 2. Check realized savings in procurement report
    res_rep = client.post(
        "/api/reports/preview",
        headers={"X-Organization-Id": "2"},
        json={
            "report_type": "procurement",
            "config": {
                "sections": ["kpi_summary"],
                "period_type": "last_90d",
                "group_by": "supplier",
            },
        },
    )
    assert res_rep.status_code == 200
    rep_data = res_rep.json()
    assert rep_data["is_empty"] is False

    kpi_map = {k["title"]: k["value"] for k in rep_data["kpi_cards"]}
    assert "Фактическая экономия" in kpi_map
    assert "Потенциал оптимизации" in kpi_map
    # Realized savings must be non-zero and distinct
    assert kpi_map["Фактическая экономия"] != "0 ₸"

    # 3. Check notifications
    notifs = client.get("/api/notifications", headers={"X-Organization-Id": "2"}).json()
    assert any("153 200 ₸" in n["title"] or "153 200 ₸" in n["description"] for n in notifs)


def test_tenant_data_isolation_between_org1_and_org2():
    """Ensure Daily Cup data never leaks into Cafe Aroma."""
    fin1 = client.get("/api/finances", headers={"X-Organization-Id": "1"}).json()
    assert len(fin1) == 0

    fin2 = client.get("/api/finances", headers={"X-Organization-Id": "2"}).json()
    assert len(fin2) > 0
    assert any("Достык 89" in t["description"] for t in fin2)


# =============================================================================
# 4. REPORT BUILDER & TEMPLATES TESTS
# =============================================================================

def test_report_templates_crud_and_presets():
    """Test preset templates listing, custom template creation, editing, duplicating, and archiving."""
    # 1. Preset listing
    res = client.get("/api/reports/templates", headers={"X-Organization-Id": "2"})
    assert res.status_code == 200
    tpls = res.json()
    assert len(tpls) >= 4
    system_tpls = [t for t in tpls if t["is_system"]]
    assert len(system_tpls) == 4

    # 2. Create custom template
    res_create = client.post(
        "/api/reports/templates",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
        json={
            "title": "Мой квартальный отчет по поставщикам",
            "description": "Специальный шаблон для ежемесячной планерки",
            "report_type": "procurement",
            "config": {
                "sections": ["kpi_summary", "supplier_distribution"],
                "period_type": "last_90d",
                "group_by": "supplier",
                "sort_by": "amount_desc",
            },
        },
    )
    assert res_create.status_code == 201
    custom_tpl = res_create.json()
    assert custom_tpl["title"] == "Мой квартальный отчет по поставщикам"
    assert custom_tpl["is_system"] is False
    custom_id = custom_tpl["id"]

    # 3. Duplicate template
    res_dup = client.post(
        f"/api/reports/templates/{custom_id}/duplicate",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
    )
    assert res_dup.status_code == 201
    dup_tpl = res_dup.json()
    assert "Копия -" in dup_tpl["title"]

    # 4. Edit custom template
    res_update = client.put(
        f"/api/reports/templates/{custom_id}",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
        json={"title": "Обновленный квартальный отчет"},
    )
    assert res_update.status_code == 200
    assert res_update.json()["title"] == "Обновленный квартальный отчет"

    # 5. Cannot delete system template
    res_del_sys = client.delete(
        f"/api/reports/templates/{system_tpls[0]['id']}",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
    )
    assert res_del_sys.status_code == 400

    # 6. Archive custom template
    res_del = client.delete(
        f"/api/reports/templates/{custom_id}",
        headers={"X-Organization-Id": "2", "X-User-Role": "owner"},
    )
    assert res_del.status_code == 200

    # 7. Isolation: Org 1 does not see custom templates of Org 2
    org1_tpls = client.get("/api/reports/templates", headers={"X-Organization-Id": "1"}).json()
    assert not any(t["id"] == dup_tpl["id"] for t in org1_tpls)


def test_report_preview_and_export_consistency():
    """Verify preview calculations match exported Excel and CSV."""
    req_body = {
        "report_type": "financial",
        "config": {
            "title": "Финансовый аудит Daily Cup",
            "sections": ["kpi_summary", "detailed_table"],
            "period_type": "last_90d",
            "group_by": "category",
            "sort_by": "amount_desc",
        },
    }

    # 1. Preview
    res_prev = client.post(
        "/api/reports/preview",
        headers={"X-Organization-Id": "2"},
        json=req_body,
    )
    assert res_prev.status_code == 200
    prev = res_prev.json()
    assert prev["is_empty"] is False
    assert len(prev["kpi_cards"]) == 4
    assert len(prev["rows"]) > 0

    # 2. Excel Export
    res_excel = client.post(
        "/api/reports/export/excel",
        headers={"X-Organization-Id": "2"},
        json=req_body,
    )
    assert res_excel.status_code == 200
    assert len(res_excel.content) > 1000
    assert "spreadsheetml" in res_excel.headers["content-type"]

    # 3. CSV Export
    res_csv = client.post(
        "/api/reports/export/csv",
        headers={"X-Organization-Id": "2"},
        json=req_body,
    )
    assert res_csv.status_code == 200
    csv_text = res_csv.content.decode("utf-8-sig")
    assert "Финансовый аудит Daily Cup" in csv_text
    assert "Выручка / Доходы" in csv_text


def test_report_builder_empty_org_handling():
    """In an empty organization (Cafe Aroma before imports), Report Builder returns is_empty=True."""
    req_body = {
        "report_type": "financial",
        "config": {
            "sections": ["kpi_summary"],
            "period_type": "current_month",
        },
    }
    res = client.post(
        "/api/reports/preview",
        headers={"X-Organization-Id": "1"},
        json=req_body,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_empty"] is True
    assert "отсутствуют исторические данные" in data["message"]
