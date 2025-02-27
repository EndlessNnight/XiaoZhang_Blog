from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ...core.database import get_db
from ...crud import movie as crud_movie
from ...schemas.movie import Movie, MovieCreate, MovieUpdate, MovieList
from ...schemas.user import User
from ...core.auth import check_admin_permission, get_current_active_user
from ...utils.tmdb import get_movie_info, get_tv_info, tmdb_client

router = APIRouter()

@router.get("/", response_model=MovieList)
async def read_movies(
    skip: int = 0,
    limit: int = 24,
    media_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud_movie.get_movies(
        db,
        skip=skip,
        limit=limit,
        media_type=media_type,
        sort_by=sort_by
    )

@router.get("/search", response_model=MovieList)
async def search_movies(
    query: str,
    skip: int = 0,
    limit: int = 24,
    db: Session = Depends(get_db)
):
    return crud_movie.search_movies(db, query, skip, limit)

@router.get("/tmdb/search/movie")
async def search_tmdb_movies(query: str):
    return await get_movie_info(query)

@router.get("/tmdb/search/tv")
async def search_tmdb_tv(query: str):
    return await get_tv_info(query)

@router.get("/tmdb/search/{media_type}")
async def search_tmdb(
    media_type: str,
    query: str = Query(..., description="搜索关键词"),
    page: int = Query(1, description="页码"),
    current_user: User = Depends(get_current_active_user)
):
    """
    搜索 TMDB 电影或电视剧
    - media_type: movie 或 tv
    - query: 搜索关键词
    - page: 页码
    """
    if media_type not in ["movie", "tv"]:
        raise HTTPException(status_code=400, detail="无效的媒体类型")
    
    if media_type == "movie":
        return await tmdb_client.search_movies(query, page)
    else:
        return await tmdb_client.search_tv(query, page)

@router.post("/", response_model=Movie)
async def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_movie.create_movie(db, movie)

@router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_movie.update_movie(db, movie_id, movie)

@router.delete("/{movie_id}")
async def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_movie.delete_movie(db, movie_id) 