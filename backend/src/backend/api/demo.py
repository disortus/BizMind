from pathlib import Path
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.demo.seed_data import reset_and_seed_db
from backend.demo.generate_demo_files import generate_all_excel_files, DEMO_DATA_DIR

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/reset")
def reset_demo_database(db: Session = Depends(get_db)):
    # Re-generate excel files if needed
    generate_all_excel_files()
    res = reset_and_seed_db(db)
    return res

@router.get("/sample-files", response_model=List[Dict[str, str]])
def list_sample_files(
    organization_id: int = Depends(get_current_organization_id),
):
    if organization_id == 2:
        return [
            {
                "filename": "dailycup_finances.xlsx",
                "name": "Финансовые операции Daily Cup (6 месяцев)",
                "import_type": "finances",
                "description": "58 записей: аренда ул. Достык, ФОТ смен бариста, регулярные закупки и выручка To-Go",
                "size": "16 КБ",
            },
            {
                "filename": "dailycup_purchases.xlsx",
                "name": "История закупок Daily Cup (история смены поставщиков)",
                "import_type": "purchases",
                "description": "25 партий: переход со стаканов PackGroup (1 420 ₸) на EcoTorg (1 230 ₸, экономия 190 ₸/упак) и оптовый кофе",
                "size": "13 КБ",
            },
            {
                "filename": "dailycup_inventory.xlsx",
                "name": "Остатки склада Daily Cup",
                "import_type": "inventory",
                "description": "10 позиций с актуальными остатками сырья, расходников и выпечки",
                "size": "10 КБ",
            },
            {
                "filename": "dailycup_supplier_prices.xlsx",
                "name": "Прайс-листы поставщиков упаковки и расходников",
                "import_type": "supplier_prices",
                "description": "8 предложений: EcoTorg, Almaty HoReCa Box, BioMilk, Syrup Direct",
                "size": "11 КБ",
            },
        ]
    else:
        return [
            {
                "filename": "historical_finances.xlsx",
                "name": "1. Исторические финансы Cafe Aroma (Excel)",
                "import_type": "finances",
                "description": "53 записи из внутренней бухгалтерии: аренда пр. Абая 45, зарплаты бариста, коммуналка, выручка",
                "size": "15 КБ",
                "path": "demo_data/onboarding/cafe_aroma/historical_finances.xlsx",
            },
            {
                "filename": "historical_purchases.xlsx",
                "name": "2. История прошлых закупок Cafe Aroma (Excel)",
                "import_type": "purchases",
                "description": "31 закупка: кофе у Coffee Roasters Hub (сентябрьский скачок до 11 500 ₸), молоко 3.2%, упаковка",
                "size": "12 КБ",
                "path": "demo_data/onboarding/cafe_aroma/historical_purchases.xlsx",
            },
            {
                "filename": "supplier_price_lists.xlsx",
                "name": "3. Прайс-листы поставщиков HoReCa (Excel)",
                "import_type": "supplier_prices",
                "description": "10 актуальных предложений: кофе Aroma Direct (10 350 ₸ вместо 11 500 ₸, экономия 1 150 ₸/кг), молоко, стаканы",
                "size": "10 КБ",
                "path": "demo_data/onboarding/cafe_aroma/supplier_price_lists.xlsx",
            },
            {
                "filename": "historical_inventory.xlsx",
                "name": "4. Начальные остатки склада Cafe Aroma (Excel)",
                "import_type": "inventory",
                "description": "10 товаров: остатки зерна (18 кг), молока (12 л), сиропов, двухслойных стаканов и чая",
                "size": "9 КБ",
                "path": "demo_data/onboarding/cafe_aroma/historical_inventory.xlsx",
            },
        ]

@router.get("/files/{filename}")
def download_sample_file(filename: str):
    allowed_files = [
        "historical_finances.xlsx",
        "historical_purchases.xlsx",
        "historical_inventory.xlsx",
        "supplier_price_lists.xlsx",
        "legacy_finances.xlsx",
        "legacy_purchases.xlsx",
        "legacy_inventory.xlsx",
        "supplier_price_list.xlsx",
        "dailycup_finances.xlsx",
        "dailycup_purchases.xlsx",
        "dailycup_inventory.xlsx",
        "dailycup_supplier_prices.xlsx",
    ]
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="Файл не найден")

    # Check dedicated onboarding directory first
    onboarding_file = DEMO_DATA_DIR / "onboarding" / "cafe_aroma" / filename
    if onboarding_file.exists():
        file_path = onboarding_file
    else:
        file_path = DEMO_DATA_DIR / filename
        if not file_path.exists():
            # Check if alias exists
            alias_map = {
                "historical_finances.xlsx": "legacy_finances.xlsx",
                "historical_purchases.xlsx": "legacy_purchases.xlsx",
                "historical_inventory.xlsx": "legacy_inventory.xlsx",
                "supplier_price_lists.xlsx": "supplier_price_list.xlsx",
                "legacy_finances.xlsx": "historical_finances.xlsx",
                "legacy_purchases.xlsx": "historical_purchases.xlsx",
                "legacy_inventory.xlsx": "historical_inventory.xlsx",
                "supplier_price_list.xlsx": "supplier_price_lists.xlsx",
            }
            if filename in alias_map:
                alias = alias_map[filename]
                if (onboarding_file.parent / alias).exists():
                    file_path = onboarding_file.parent / alias
                elif (DEMO_DATA_DIR / alias).exists():
                    file_path = DEMO_DATA_DIR / alias

    if not file_path.exists():
        generate_all_excel_files()

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на сервере")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

