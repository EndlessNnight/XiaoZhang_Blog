from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

class MovieBase(BaseModel):
    tmdb_id: int
    title: str
    original_title: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    type: str  # movie/tv
    sub_type: Optional[str] = None
    genres: Optional[str] = None
    watch_status: Optional[str] = None
    rating: Optional[float] = None
    comment: Optional[str] = None
    watch_date: Optional[date] = None

class MovieCreate(MovieBase):
    pass

class MovieUpdate(MovieBase):
    tmdb_id: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None

class Movie(MovieBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MovieList(BaseModel):
    items: List[Movie]
    total: int

    class Config:
        from_attributes = True 