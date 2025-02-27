from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .user import User

class CommentBase(BaseModel):
    content: str
    article_id: int
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    user: User
    replies: List['Comment'] = []

    class Config:
        from_attributes = True 