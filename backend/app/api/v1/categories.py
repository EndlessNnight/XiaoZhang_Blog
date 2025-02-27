from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...crud import category as crud_category
from ...schemas.category import Category, CategoryCreate, CategoryUpdate
from ...schemas.user import User
from ...core.auth import check_admin_permission

router = APIRouter()

@router.get("/", response_model=List[Category])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud_category.get_categories(db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=Category)
async def read_category(category_id: int, db: Session = Depends(get_db)):
    category = crud_category.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@router.post("/", response_model=Category)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_category.create_category(db, category)

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_category.update_category(db, category_id, category)

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_category.delete_category(db, category_id) 