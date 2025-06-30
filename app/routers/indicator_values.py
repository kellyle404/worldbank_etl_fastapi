from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.indicator_values import IndicatorValueCreate, IndicatorValueOut, IndicatorValueUpdate
from app.models.models import IndicatorValue
from app.db.db import get_db
from app.utils.logger import logger  
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/indicator-values", tags=["IndicatorValues"])

@router.get("/", response_model=List[IndicatorValueOut])
def get_indicator_values(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        indicator_id: Optional[int] = Query(None),
        country_id: Optional[int] = Query(None)
):
    logger.info(
        f"GET /indicator-values called: page={page}, limit={limit}, "
        f"indicator_id={indicator_id}, country_id={country_id}"
    )
    query = db.query(IndicatorValue)
    if indicator_id:
        query = query.filter(IndicatorValue.indicator_id == indicator_id)
    if country_id:
        query = query.filter(IndicatorValue.country_id == country_id)
    
    indicator_values = query.offset((page - 1) * limit).limit(limit).all()
    logger.info(f"Returning {len(indicator_values)} indicator values")
    return indicator_values

@router.get("/{iv_id}", response_model=IndicatorValueOut)
def get_indicator_value(iv_id: int, db: Session = Depends(get_db)):
    logger.info(f"GET /indicator-values/{iv_id} called")
    iv = db.query(IndicatorValue).filter(IndicatorValue.id == iv_id).first()
    if not iv:
        logger.warning(f"Indicator value with id={iv_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator value not found")
    logger.info(f"Indicator value {iv_id} found")
    return iv

@router.post("/", response_model=IndicatorValueOut, status_code=status.HTTP_201_CREATED)
def create_indicator_value(iv_in: IndicatorValueCreate, db: Session = Depends(get_db)):
    logger.info(f"POST /indicator-values called: indicator_id={iv_in.indicator_id}, country_id={iv_in.country_id}, date={iv_in.date}, value={iv_in.value}")
    iv = IndicatorValue(
        indicator_id=iv_in.indicator_id,
        country_id=iv_in.country_id,
        date=iv_in.date,
        value=iv_in.value
    )
    db.add(iv)
    try:
        db.commit()
        db.refresh(iv)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate indicator value")
    logger.info(f"Created new indicator value with id={iv.id}")
    return iv


@router.put("/{iv_id}", response_model=IndicatorValueOut)
def update_indicator_value(iv_id: int, iv_in: IndicatorValueUpdate, db: Session = Depends(get_db)):
    logger.info(f"PUT /indicator-values/{iv_id} called with value={iv_in.value}")
    iv = db.query(IndicatorValue).filter(IndicatorValue.id == iv_id).first()
    if not iv:
        logger.warning(f"Indicator value with id={iv_id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator value not found")
    
    if iv_in.value is not None:
        logger.info(f"Updating indicator value {iv_id} from {iv.value} to {iv_in.value}")
        iv.value = iv_in.value
    
    db.commit()
    db.refresh(iv)
    logger.info(f"Indicator value {iv_id} updated successfully")
    return iv

@router.delete("/{iv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator_value(iv_id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /indicator-values/{iv_id} called")
    iv = db.query(IndicatorValue).filter(IndicatorValue.id == iv_id).first()
    if not iv:
        logger.warning(f"Indicator value with id={iv_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator value not found")
    
    db.delete(iv)
    db.commit()
    logger.info(f"Indicator value {iv_id} deleted successfully")
    return None