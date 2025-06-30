from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.topics import TopicCreate, TopicOut, TopicUpdate
from app.models.models import Topic
from app.db.db import get_db
from app.utils.logger import logger
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.get("/", response_model=List[TopicOut])
def get_topics(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query("", description="Search topics by name")
):
    logger.info(f"GET /topics called with page={page}, limit={limit}, search='{search}'")
    query = db.query(Topic)
    if search:
        query = query.filter(Topic.name.ilike(f"%{search}%"))
    topics = query.offset((page - 1) * limit).limit(limit).all()
    logger.info(f"Returning {len(topics)} topics")
    return topics

@router.get("/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    logger.info(f"GET /topics/{topic_id} called")
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        logger.warning(f"Topic with id={topic_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    logger.info(f"Topic with id={topic_id} found: {topic.name}")
    return topic

@router.post("/", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic(topic_in: TopicCreate, db: Session = Depends(get_db)):
    logger.info(f"POST /topics called with name={topic_in.name}")
    topic = Topic(name=topic_in.name)
    db.add(topic)
    try:
        db.commit()
        db.refresh(topic)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic name already exists")
    logger.info(f"Topic created with id={topic.id}")
    return topic


@router.put("/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, topic_in: TopicUpdate, db: Session = Depends(get_db)):
    logger.info(f"PUT /topics/{topic_id} called with name={topic_in.name}")
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        logger.warning(f"Topic with id={topic_id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    topic.name = topic_in.name
    db.commit()
    db.refresh(topic)
    logger.info(f"Topic with id={topic_id} updated successfully")
    return topic

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /topics/{topic_id} called")
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        logger.warning(f"Topic with id={topic_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    db.delete(topic)
    db.commit()
    logger.info(f"Topic with id={topic_id} deleted successfully")
    return None