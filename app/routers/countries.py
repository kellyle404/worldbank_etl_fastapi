from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.countries import CountryCreate, CountryOut, CountryUpdate
from app.models.models import Country
from app.db.db import get_db
from app.utils.logger import logger   
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/countries", tags=["Countries"])

@router.get("/", response_model=List[CountryOut])
def get_countries(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query("", description="Search countries by name or ISO3")
):
    logger.info(f"GET /countries called with page={page}, limit={limit}, search='{search}'")
    query = db.query(Country)
    if search:
        query = query.filter(
            (Country.name.ilike(f"%{search}%")) |
            (Country.iso3.ilike(f"%{search}%"))
        )
    countries = query.offset((page - 1) * limit).limit(limit).all()
    logger.info(f"Returning {len(countries)} countries")
    return countries

@router.get("/{country_id}", response_model=CountryOut)
def get_country(country_id: int, db: Session = Depends(get_db)):
    logger.info(f"GET /countries/{country_id} called")
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        logger.warning(f"Country with id={country_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    logger.info(f"Country with id={country_id} found: {country.name}")
    return country

@router.post("/", response_model=CountryOut, status_code=status.HTTP_201_CREATED)
def create_country(country_in: CountryCreate, db: Session = Depends(get_db)):
    logger.info(f"POST /countries called with data: iso3={country_in.iso3}, name={country_in.name}")
    country = Country(iso3=country_in.iso3, name=country_in.name, region=country_in.region)
    db.add(country)
    try:
        db.commit()
        db.refresh(country)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISO3 already exists")
    logger.info(f"Country created with id={country.id}")
    return country

@router.put("/{country_id}", response_model=CountryOut)
def update_country(country_id: int, country_in: CountryUpdate, db: Session = Depends(get_db)):
    logger.info(f"PUT /countries/{country_id} called with data: {country_in}")
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        logger.warning(f"Country with id={country_id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    if country_in.name is not None:
        logger.info(f"Updating name to {country_in.name}")
        country.name = country_in.name
    if country_in.region is not None:
        logger.info(f"Updating region to {country_in.region}")
        country.region = country_in.region

    db.commit()
    db.refresh(country)
    logger.info(f"Country with id={country_id} updated successfully")
    return country

@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /countries/{country_id} called")
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        logger.warning(f"Country with id={country_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    db.delete(country)
    db.commit()
    logger.info(f"Country with id={country_id} deleted successfully")
    return None