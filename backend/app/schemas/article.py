from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .category import Category
from .comment import Comment

class ArticleBase(BaseModel):
    title: str
    content: str
    cover_image: Optional[str] = None
    author_id: int
    category_id: Optional[int] = None
    is_hidden: bool = False

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    views_count: int = 0
    likes_count: int
    comments_count: int = 0
    category: Optional[Category] = None
    comments: List[Comment] = []

    class Config:
        from_attributes = True

class ArticleList(BaseModel):
    items: list[Article]
    total: int 