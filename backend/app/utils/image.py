import os
import uuid
from fastapi import UploadFile
from PIL import Image
from ..core.config import settings

async def save_image(file: UploadFile, folder: str = "uploads") -> str:
    """保存上传的图片"""
    # 确保目录存在
    upload_dir = os.path.join(settings.UPLOAD_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # 读取并压缩图片
        image = Image.open(await file.read())
        
        # 如果图片太大，进行压缩
        if os.path.getsize(file.file) > settings.MAX_UPLOAD_SIZE:
            image.thumbnail((800, 800))
        
        # 保存图片
        image.save(file_path, quality=85, optimize=True)
        
        # 返回相对路径
        return f"/{folder}/{unique_filename}"
    except Exception as e:
        raise Exception(f"保存图片失败: {str(e)}")

def delete_image(image_path: str) -> bool:
    """删除图片"""
    if not image_path:
        return False
    
    try:
        # 获取完整路径
        full_path = os.path.join(settings.UPLOAD_DIR, image_path.lstrip('/'))
        
        # 检查文件是否存在
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False 