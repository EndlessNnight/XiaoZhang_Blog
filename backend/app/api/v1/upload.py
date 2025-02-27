from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from ...core.auth import get_current_active_user
from ...schemas.user import User
from ...core.config import settings
import os
import uuid
from datetime import datetime
from PIL import Image
import io

router = APIRouter()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image(file: UploadFile) -> bool:
    """验证上传的文件"""
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 验证是否为有效的图片文件
    try:
        image_data = file.file.read()
        if len(image_data) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        image = Image.open(io.BytesIO(image_data))
        image.verify()  # 验证图片完整性
        
        # 重置文件指针
        file.file.seek(0)
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail="无效的图片文件")

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传图片
    - 支持的格式：JPG, JPEG, PNG, GIF, WEBP
    - 最大文件大小：5MB
    - 返回图片URL
    """
    try:
        validate_image(file)
        
        # 生成文件名
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(os.getcwd(), settings.UPLOAD_DIR)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        # 返回文件URL
        return JSONResponse({
            "url": f"/uploads/{filename}",
            "filename": filename
        })
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}") 