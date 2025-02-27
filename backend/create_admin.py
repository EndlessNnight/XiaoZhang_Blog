from app.database import SessionLocal
import app.models as models
from app.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    
    # 检查管理员是否已存在
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if admin:
        print("管理员用户已存在")
        return
    
    try:
        # 创建管理员用户
        admin_user = models.User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            avatar="default_avatar_url"  # 设置默认头像 URL
        )
        
        db.add(admin_user)
        db.commit()
        print("管理员用户创建成功")
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 