from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.schemas.schemas import (
    ImportPreviewResult,
    ImportExecuteResult,
    ImportBatchResponse,
)
from backend.services.import_service import ImportService

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/preview", response_model=ImportPreviewResult)
async def preview_import(
    file: UploadFile = File(...),
    import_type: str = Form("finances"),
):
    content = await file.read()
    return ImportService.preview_file(content, file.filename or "upload.xlsx", import_type)

@router.post("/execute", response_model=ImportExecuteResult)
async def execute_import(
    file: UploadFile = File(...),
    import_type: str = Form("finances"),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    content = await file.read()
    return ImportService.execute_import(
        db=db,
        file_bytes=content,
        filename=file.filename or "upload.xlsx",
        import_type=import_type,
        organization_id=organization_id,
    )

@router.get("/batches", response_model=List[ImportBatchResponse])
def get_batches(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    return ImportService.get_batches(db=db, organization_id=organization_id)
