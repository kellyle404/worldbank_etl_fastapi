from pydantic import BaseModel
from typing import Optional, List

class TopicBase(BaseModel):
    name: str

class TopicCreate(TopicBase):
    pass

class TopicUpdate(TopicBase):
    pass

class TopicOut(TopicBase):
    id: int

    class Config:
        from_attributes = True
