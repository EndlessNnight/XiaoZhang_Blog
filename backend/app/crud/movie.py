from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.movie import Movie
from ..schemas.movie import MovieCreate, MovieUpdate

def get_movie(db: Session, movie_id: int) -> Optional[Movie]:
    return db.query(Movie).filter(
        Movie.id == movie_id,
        Movie.is_deleted == False
    ).first()

def get_movies(
    db: Session,
    skip: int = 0,
    limit: int = 24,
    media_type: Optional[str] = None,
    sort_by: Optional[str] = None
):
    query = db.query(Movie).filter(Movie.is_deleted == False)
    
    # 筛选媒体类型
    if media_type:
        query = query.filter(Movie.type == media_type)
    
    # 排序
    if sort_by:
        if sort_by == "watch_date_desc":
            query = query.order_by(Movie.watch_date.desc())
        elif sort_by == "watch_date_asc":
            query = query.order_by(Movie.watch_date.asc())
        elif sort_by == "rating_desc":
            query = query.order_by(Movie.rating.desc())
        elif sort_by == "release_date_desc":
            query = query.order_by(Movie.release_date.desc())
    else:
        # 默认按观看日期降序
        query = query.order_by(Movie.watch_date.desc())
    
    total = query.count()
    movies = query.offset(skip).limit(limit).all()
    
    return {
        "items": movies,
        "total": total
    }

def create_movie(db: Session, movie: MovieCreate):
    db_movie = Movie(**movie.dict())
    try:
        db.add(db_movie)
        db.commit()
        db.refresh(db_movie)
        return db_movie
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def update_movie(db: Session, movie_id: int, movie: MovieUpdate):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="影视条目不存在")
    
    try:
        for key, value in movie.dict(exclude_unset=True).items():
            setattr(db_movie, key, value)
        db_movie.updated_at = datetime.now()
        db.commit()
        db.refresh(db_movie)
        return db_movie
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_movie(db: Session, movie_id: int):
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="影视条目不存在")
    
    try:
        db_movie.is_deleted = True
        db_movie.deleted_at = datetime.now()
        db.commit()
        return {"message": "影视条目已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def search_movies(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 24
):
    search_query = f"%{query}%"
    try:
        base_query = db.query(Movie).filter(
            Movie.is_deleted == False,
            or_(
                Movie.title.ilike(search_query),
                Movie.original_title.ilike(search_query),
                Movie.overview.ilike(search_query)
            )
        )
        
        total = base_query.count()
        movies = base_query.order_by(Movie.rating.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return {
            "items": movies,
            "total": total
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        ) 