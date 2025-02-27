from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, List
from ..models.comment import Comment
from ..schemas.comment import CommentCreate
from ..models.article import Article

def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    return db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()

def get_comments(
    db: Session,
    article_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[Comment]:
    return db.query(Comment)\
        .filter(
            Comment.article_id == article_id,
            Comment.is_deleted == False,
            Comment.parent_id == None  # 只获取顶级评论
        )\
        .order_by(Comment.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def count_article_comments(db: Session, article_id: int) -> int:
    """计算文章的有效评论数（未删除的评论）"""
    return db.query(Comment).filter(
        Comment.article_id == article_id,
        Comment.is_deleted == False
    ).count()

def create_comment(db: Session, comment: CommentCreate, user_id: int):
    try:
        db_comment = Comment(
            **comment.dict(),
            user_id=user_id
        )
        db.add(db_comment)
        db.commit()
        
        # 更新文章评论数
        article = db.query(Article).filter(Article.id == comment.article_id).first()
        if article:
            # 重新计算评论数
            article.comments_count = count_article_comments(db, article.id)
        
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_comment(db: Session, comment_id: int, user_id: int):
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    if db_comment.user_id != user_id and not db_comment.user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限删除此评论")
    
    try:
        # 递归删除所有子评论
        def delete_replies(comment):
            for reply in comment.replies:
                if not reply.is_deleted:
                    reply.is_deleted = True
                    reply.deleted_at = datetime.now()
                    delete_replies(reply)
        
        # 删除所有子评论
        delete_replies(db_comment)
        
        # 软删除评论
        db_comment.is_deleted = True
        db_comment.deleted_at = datetime.now()
        db.commit()
        
        # 更新文章评论数
        if db_comment.article:
            # 重新计算评论数（包括已删除的子评论）
            db_comment.article.comments_count = count_article_comments(db, db_comment.article_id)
        
        db.commit()
        return {"message": "评论已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 