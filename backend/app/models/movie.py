from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from ..core.database import Base
from .mixins import SoftDeleteMixin

class Movie(Base, SoftDeleteMixin):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String(200), nullable=False)
    original_title = Column(String(200))
    poster_path = Column(String(500))
    backdrop_path = Column(String(500))
    overview = Column(Text)
    release_date = Column(Date)
    type = Column(String(50))
    sub_type = Column(String(50))
    genres = Column(String(200))
    
    # 观看信息
    watch_status = Column(String(20))
    rating = Column(Integer)
    comment = Column(String(140))
    watch_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 