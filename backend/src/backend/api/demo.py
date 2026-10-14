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
                "name": "Финансовые операции Daily Cup (5 месяцев)",
                "import_type": "finances",
                "description": "48 записей: аренда ул. Достык, ФОТ бариста, закупки упаковки и выручка сети To-Go",
                "size": "16 КБ",
            },
            {
                "filename": "dailycup_purchases.xlsx",
                "name": "История закупок Daily Cup (скачок цен на стаканы)",
                "import_type": "purchases",
                "description": "24 партии: динамика закупок стаканов Kraft 250мл (прыжок с 1 200 до 1 420 ₸), молока Parmalat и кофе",
                "size": "13 КБ",
            },
            {
                "filename": "dailycup_inventory.xlsx",
                "name": "Остатки склада Daily Cup",
                "import_type": "inventory",
                "description": "10 позиций с критическим остатком держателей стаканов (6 упак при норме 12) и растительного молока (8л)",
                "size": "10 КБ",
            },
            {
                "filename": "dailycup_supplier_prices.xlsx",
                "name": "Прайс-лист поставщиков упаковки и расходников",
                "import_type": "supplier_prices",
                "description": "8 предложений: EcoTorg (стаканы 1 230 ₸ вместо 1 420 ₸, выгода 190 ₸/упак), BioMilk, Syrup Direct",
                "size": "11 КБ",
            },
        ]
    else:
        return [
            {
                "filename": "legacy_finances.xlsx",
                "name": "Финансовые операции Cafe Aroma (4 месяца)",
                "import_type": "finances",
                "description": "53 записи: аренда ул. Абая, зарплаты, закупки сырья, коммунальные услуги, выручка",
                "size": "15 КБ",
            },
            {
                "filename": "legacy_purchases.xlsx",
                "name": "История закупок Cafe Aroma (скачок цен на кофе)",
                "import_type": "purchases",
                "description": "31 запись: динамика закупок кофе (прыжок до 11 500 ₸), молока 3.2%, сиропов и стаканов",
                "size": "12 КБ",
            },
            {
                "filename": "legacy_inventory.xlsx",
                "name": "Остатки склада Cafe Aroma",
                "import_type": "inventory",
                "description": "10 товаров с критическими остатками по молоку (12л при норме 25) и крышкам (8 упак)",
                "size": "9 КБ",
            },
            {
                "filename": "supplier_price_list.xlsx",
                "name": "Прайс-лист альтернативных поставщиков сырья",
                "import_type": "supplier_prices",
                "description": "10 предложений от Aroma Direct (кофе 10 350 ₸ вместо 11 500 ₸), Qazaq Milk Line, Global Pack",
                "size": "10 КБ",
            },
        ]

@router.get("/files/{filename}")
def download_sample_file(filename: str):
    allowed_files = [
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

    file_path = DEMO_DATA_DIR / filename
    if not file_path.exists():
        generate_all_excel_files()

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
