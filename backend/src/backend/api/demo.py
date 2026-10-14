from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
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
def list_sample_files():
    files_meta = [
        {
            "filename": "legacy_finances.xlsx",
            "name": "Финансовые операции (4 месяца)",
            "import_type": "finances",
            "description": "53 записи: аренда, зарплаты, закупки сырья, коммунальные услуги, выручка",
            "size": "15 КБ",
        },
        {
            "filename": "legacy_purchases.xlsx",
            "name": "История закупок кофейни",
            "import_type": "purchases",
            "description": "31 запись: динамика закупок кофе (с прыжком цены до 11 500 ₸), молока, сиропов и упаковки",
            "size": "12 КБ",
        },
        {
            "filename": "legacy_inventory.xlsx",
            "name": "Остатки на складе и неснижаемый минимум",
            "import_type": "inventory",
            "description": "10 товаров с критическими остатками по молоку (12л) и крышкам (8 упак)",
            "size": "9 КБ",
        },
        {
            "filename": "supplier_price_list.xlsx",
            "name": "Прайс-лист альтернативных поставщиков",
            "import_type": "supplier_prices",
            "description": "10 предложений от Aroma Direct (кофе 10 350 ₸), Qazaq Milk Line, Global Pack и др.",
            "size": "10 КБ",
        },
    ]
    return files_meta

@router.get("/files/{filename}")
def download_sample_file(filename: str):
    allowed_files = [
        "legacy_finances.xlsx",
        "legacy_purchases.xlsx",
        "legacy_inventory.xlsx",
        "supplier_price_list.xlsx",
    ]
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="Файл не найден")

    file_path = DEMO_DATA_DIR / filename
    if not file_path.exists():
        # Regenerate if missing
        generate_all_excel_files()

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
