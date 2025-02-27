from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.article import Article
from ..schemas.article import ArticleCreate, ArticleUpdate
from ..crud.comment import get_comments

def get_article(db: Session, article_id: int) -> Optional[Article]:
    return db.query(Article).filter(
        Article.id == article_id,
        Article.is_deleted == False
    ).first()

def get_articles(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    include_hidden: bool = False
):
    query = db.query(Article).filter(Article.is_deleted == False)
    
    if category_id:
        query = query.filter(Article.category_id == category_id)
    
    if not include_hidden:
        query = query.filter(Article.is_hidden == False)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_filter),
                Article.content.ilike(search_filter)
            )
        )
    
    total = query.count()
    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()
    # articles.comments = get_comments( db, article_id=articles.id, skip=0, limit=50)
    return {
        "items": articles,
        "total": total
    }

def create_article(db: Session, article: ArticleCreate):
    db_article = Article(**article.dict())
    try:
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def update_article(db: Session, article_id: int, article: ArticleUpdate):
    db_article = get_article(db, article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    try:
        for key, value in article.dict(exclude_unset=True).items():
            setattr(db_article, key, value)
        db_article.updated_at = datetime.now()
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_article(db: Session, article_id: int):
    db_article = get_article(db, article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    try:
        db_article.is_deleted = True
        db_article.deleted_at = datetime.now()
        db.commit()
        return {"message": "文章已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def increment_article_view(db: Session, article_id: int):
    try:
        article = get_article(db, article_id)
        if article:
            article.views_count += 1
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False

def get_articles_count(db: Session) -> int:
    """获取文章总数"""
    return db.query(func.count(Article.id)).scalar()

def get_articles(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    category_id: int = None,
    search: str = None,
    include_hidden: bool = False
) -> list[Article]:
    """获取文章列表"""
    query = db.query(Article)
    
    if category_id:
        query = query.filter(Article.category_id == category_id)
    
    if search:
        query = query.filter(Article.title.ilike(f"%{search}%"))
    
    if not include_hidden:
        query = query.filter(Article.is_hidden == False)
    
    return query.offset(skip).limit(limit).all() 