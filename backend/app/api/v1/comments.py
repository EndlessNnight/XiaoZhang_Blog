from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...crud import comment as crud_comment
from ...schemas.comment import Comment, CommentCreate
from ...schemas.user import User
from ...core.auth import get_current_active_user

router = APIRouter()

@router.get("/{article_id}", response_model=List[Comment])
async def read_comments(
    article_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return crud_comment.get_comments(
        db,
        article_id=article_id,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=Comment)
async def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud_comment.create_comment(db, comment, current_user.id)

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud_comment.delete_comment(db, comment_id, current_user.id) 