from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.indicators_meta import IndicatorMetaCreate, IndicatorMetaOut, IndicatorMetaUpdate
from app.models.models import IndicatorMeta
from app.db.db import get_db
from app.utils.logger import logger
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/indicators", tags=["Indicators"])

@router.get("/", response_model=List[IndicatorMetaOut])
def get_indicators(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query("", description="Search indicators by name or code")
):
    logger.info(f"GET /indicators called with page={page}, limit={limit}, search='{search}'")
    query = db.query(IndicatorMeta)
    if search:
        query = query.filter(
            (IndicatorMeta.name.ilike(f"%{search}%")) |
            (IndicatorMeta.code.ilike(f"%{search}%"))
        )
    indicators = query.offset((page - 1) * limit).limit(limit).all()
    logger.info(f"Returning {len(indicators)} indicators")
    return indicators

@router.get("/{indicator_id}", response_model=IndicatorMetaOut)
def get_indicator(indicator_id: int, db: Session = Depends(get_db)):
    logger.info(f"GET /indicators/{indicator_id} called")
    indicator = db.query(IndicatorMeta).filter(IndicatorMeta.id == indicator_id).first()
    if not indicator:
        logger.warning(f"Indicator with id={indicator_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")
    logger.info(f"Indicator with id={indicator_id} found: {indicator.name}")
    return indicator

@router.post("/", response_model=IndicatorMetaOut, status_code=status.HTTP_201_CREATED)
def create_indicator(indicator_in: IndicatorMetaCreate, db: Session = Depends(get_db)):
    logger.info(f"POST /indicators called with code={indicator_in.code}, name={indicator_in.name}")
    indicator = IndicatorMeta(
        code=indicator_in.code,
        name=indicator_in.name,
        topic_id=indicator_in.topic_id,
        source_note=indicator_in.source_note
    )
    db.add(indicator)
    try:
        db.commit()
        db.refresh(indicator)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Indicator code already exists")
    logger.info(f"Indicator created with id={indicator.id}")
    return indicator


@router.put("/{indicator_id}", response_model=IndicatorMetaOut)
def update_indicator(indicator_id: int, indicator_in: IndicatorMetaUpdate, db: Session = Depends(get_db)):
    logger.info(f"PUT /indicators/{indicator_id} called with data: {indicator_in}")
    indicator = db.query(IndicatorMeta).filter(IndicatorMeta.id == indicator_id).first()
    if not indicator:
        logger.warning(f"Indicator with id={indicator_id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")
    if indicator_in.name is not None:
        indicator.name = indicator_in.name
    if indicator_in.topic_id is not None:
        indicator.topic_id = indicator_in.topic_id
    if indicator_in.source_note is not None:
        indicator.source_note = indicator_in.source_note
    db.commit()
    db.refresh(indicator)
    logger.info(f"Indicator with id={indicator_id} updated successfully")
    return indicator

@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(indicator_id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /indicators/{indicator_id} called")
    indicator = db.query(IndicatorMeta).filter(IndicatorMeta.id == indicator_id).first()
    if not indicator:
        logger.warning(f"Indicator with id={indicator_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")
    db.delete(indicator)
    db.commit()
    logger.info(f"Indicator with id={indicator_id} deleted successfully")
    return None
