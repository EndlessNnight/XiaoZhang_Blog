from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...crud import article as crud_article
from ...schemas.article import Article, ArticleCreate, ArticleUpdate, ArticleList
from ...schemas.user import User
from ...core.auth import get_current_active_user, check_admin_permission

router = APIRouter()

@router.get("/", response_model=ArticleList)
async def get_articles(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    articles = crud_article.get_articles(db, skip=skip, limit=limit)
    total = crud_article.get_articles_count(db)
    return {
        "items": articles,
        "total": total
    }

@router.get("/{article_id}", response_model=Article)
async def read_article(article_id: int, db: Session = Depends(get_db)):
    article = crud_article.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    crud_article.increment_article_view(db, article_id)
    return article

@router.post("/", response_model=Article)
async def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_article.create_article(db, article)

@router.put("/{article_id}", response_model=Article)
async def update_article(
    article_id: int,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_article.update_article(db, article_id, article)

@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_article.delete_article(db, article_id) 