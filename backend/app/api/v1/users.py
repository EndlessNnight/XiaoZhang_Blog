from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.security import create_access_token
from ...crud import user as crud_user
from ...schemas.user import User, UserCreate, UserUpdate
from ...utils.email import send_verification_email, verify_code
from ...core.auth import get_current_user, get_current_active_user, check_admin_permission

router = APIRouter()

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud_user.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    return crud_user.create_user(db, user)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    result = crud_user.update_user(db, user_id, user, current_user.id)
    return result["user"]

@router.post("/send-verification")
async def send_verification(email: str):
    return await send_verification_email(email)

@router.post("/verify-email")
async def verify_email(email: str, code: str):
    if verify_code(email, code):
        return {"message": "验证成功"}
    raise HTTPException(status_code=400, detail="验证码无效或已过期") 