import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from backend.database import get_db
from backend.api.deps import get_current_organization_id, get_current_user, require_roles, log_activity
from backend.models.models import User
from backend.schemas.schemas import (
    ReportTemplateResponse,
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportPreviewRequest,
    ReportPreviewResponse,
)
from backend.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/templates", response_model=List[ReportTemplateResponse])
def get_templates(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    """
    Returns system preset report templates and custom templates created for the organization.
    """
    return ReportService.get_templates(db=db, organization_id=organization_id)


@router.post("/templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    data: ReportTemplateCreate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    """
    Creates a new custom report template for the current organization.
    """
    template = ReportService.create_template(
        db=db,
        organization_id=organization_id,
        user_id=user.id,
        data=data,
    )
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="create_report_template",
        entity_type="report_template",
        entity_id=str(template.id),
        details=f"Создан шаблон отчёта: «{template.title}» ({template.report_type})",
    )
    return template


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
def get_template(
    template_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    template = ReportService.get_template(db=db, organization_id=organization_id, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон отчёта не найден")
    return template


@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
def update_template(
    template_id: int,
    data: ReportTemplateUpdate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    try:
        updated = ReportService.update_template(
            db=db,
            organization_id=organization_id,
            template_id=template_id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated:
        raise HTTPException(status_code=404, detail="Шаблон не найден или недоступен для изменения")

    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="update_report_template",
        entity_type="report_template",
        entity_id=str(template_id),
        details=f"Обновлен шаблон отчёта #{template_id}: {updated.title}",
    )
    return updated


@router.post("/templates/{template_id}/duplicate", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
def duplicate_template(
    template_id: int,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    copy_tpl = ReportService.duplicate_template(
        db=db,
        organization_id=organization_id,
        user_id=user.id,
        template_id=template_id,
    )
    if not copy_tpl:
        raise HTTPException(status_code=404, detail="Исходный шаблон не найден")

    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="duplicate_report_template",
        entity_type="report_template",
        entity_id=str(copy_tpl.id),
        details=f"Создана копия шаблона #{template_id} -> #{copy_tpl.id} («{copy_tpl.title}»)",
    )
    return copy_tpl


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    try:
        success = ReportService.delete_template(
            db=db,
            organization_id=organization_id,
            template_id=template_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="archive_report_template",
        entity_type="report_template",
        entity_id=str(template_id),
        details=f"Шаблон #{template_id} архивирован",
    )
    return {"status": "success", "message": f"Шаблон #{template_id} успешно архивирован"}


@router.post("/preview", response_model=ReportPreviewResponse)
def preview_report(
    payload: ReportPreviewRequest,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    """
    Generates preview data (KPI cards, aggregated tables, charts) from dynamic configuration.
    """
    config_dict = payload.config.model_dump()
    return ReportService.generate_report_data(
        db=db,
        organization_id=organization_id,
        report_type=payload.report_type,
        config=config_dict,
    )


@router.post("/export/excel")
def export_excel(
    payload: ReportPreviewRequest,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    """
    Exports report matching the preview to styled Microsoft Excel (.xlsx) format.
    """
    config_dict = payload.config.model_dump()
    file_bytes = ReportService.export_report_excel(
        db=db,
        organization_id=organization_id,
        report_type=payload.report_type,
        config=config_dict,
    )

    filename = f"report_{payload.report_type}_{organization_id}.xlsx"
    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/csv")
def export_csv(
    payload: ReportPreviewRequest,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    """
    Exports report data to CSV format with semicolon separator.
    """
    config_dict = payload.config.model_dump()
    csv_text = ReportService.export_report_csv(
        db=db,
        organization_id=organization_id,
        report_type=payload.report_type,
        config=config_dict,
    )

    filename = f"report_{payload.report_type}_{organization_id}.csv"
    return Response(
        content=csv_text.encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
