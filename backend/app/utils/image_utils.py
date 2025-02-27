from PIL import Image
import os

def compress_image(input_path: str, max_size_mb: float = 2.0) -> None:
    """压缩图片到指定大小以下"""
    img = Image.open(input_path)
    
    # 如果是 PNG，转换为 JPEG 以获得更好的压缩率
    if img.format == 'PNG':
        img = img.convert('RGB')
    
    # 初始质量
    quality = 95
    while os.path.getsize(input_path) > max_size_mb * 1024 * 1024 and quality > 20:
        img.save(input_path, 'JPEG', quality=quality)
        quality -= 5

def validate_image(file_path: str) -> bool:
    """验证文件是否为有效的图片文件"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except:
        return False 