from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password
import logging

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def update_user(db: Session, user_id: int, user: UserUpdate, current_user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    try:
        need_relogin = False
        update_data = user.dict(exclude_unset=True)
        
        # 检查管理员权限变更
        if 'is_admin' in update_data and db_user.is_admin and not update_data['is_admin']:
            admin_count = db.query(User).filter(User.is_admin == True).count()
            if admin_count <= 1:
                # 如果是最后一个管理员，移除 is_admin 字段，但保留其他更新
                update_data.pop('is_admin')
                # 可以添加一个警告信息
                # logging.warning(f"尝试移除最后一个管理员的权限 (user_id: {user_id})")
        
        # 处理密码更新
        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
            if user_id == current_user_id:
                need_relogin = True
        
        # 检查是否需要重新登录
        if user_id == current_user_id and any(key in update_data for key in ['username', 'email']):
            need_relogin = True
        
        # 更新用户信息
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        return {"user": db_user, "need_relogin": need_relogin}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 