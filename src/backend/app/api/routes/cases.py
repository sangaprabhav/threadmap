"""Case API routes — investigation management."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.case import CaseOut, CaseCreateRequest, CaseUpdateRequest, CaseNoteRequest
from app.schemas.common import PaginatedResponse
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=PaginatedResponse)
async def list_cases(
    status: str | None = None,
    priority: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await case_service.list_cases(
        db, status=status, priority=priority, offset=offset, limit=limit,
    )
    return PaginatedResponse(
        items=[CaseOut.model_validate(i) for i in items],
        total=total, offset=offset, limit=limit,
    )


@router.post("", response_model=CaseOut)
async def create_case(req: CaseCreateRequest, db: AsyncSession = Depends(get_db)):
    case = await case_service.create_case(
        db,
        title=req.title,
        description=req.description,
        priority=req.priority,
        tags=req.tags,
        category=req.category,
        content_ids=req.content_ids,
        actor_ids=req.actor_ids,
        entity_ids=req.entity_ids,
    )
    return case


@router.get("/{case_id}", response_model=CaseOut)
async def get_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await case_service.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}", response_model=CaseOut)
async def update_case(
    case_id: uuid.UUID, req: CaseUpdateRequest, db: AsyncSession = Depends(get_db),
):
    case = await case_service.update_case(
        db, case_id, **req.model_dump(exclude_unset=True),
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/notes", response_model=CaseOut)
async def add_note(
    case_id: uuid.UUID, req: CaseNoteRequest, db: AsyncSession = Depends(get_db),
):
    case = await case_service.add_case_note(
        db, case_id, text=req.text, note_type=req.note_type,
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
