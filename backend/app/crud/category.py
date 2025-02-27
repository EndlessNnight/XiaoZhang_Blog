from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, List
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate

def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category)\
        .filter(Category.is_deleted == False)\
        .order_by(Category.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(**category.dict())
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def update_category(db: Session, category_id: int, category: CategoryUpdate):
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    try:
        for key, value in category.dict(exclude_unset=True).items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查是否有关联的文章
    if db_category.articles:
        raise HTTPException(status_code=400, detail="该分类下还有文章，无法删除")
    
    try:
        db_category.is_deleted = True
        db_category.deleted_at = datetime.now()
        db.commit()
        return {"message": "分类已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 