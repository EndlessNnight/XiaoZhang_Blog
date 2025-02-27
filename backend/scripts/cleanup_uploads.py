import os
import time
from datetime import datetime, timedelta

UPLOAD_DIR = "../uploads"
MAX_AGE_DAYS = 30  # 文件保存的最大天数

def cleanup_old_files():
    """清理超过指定天数的上传文件"""
    now = time.time()
    max_age = timedelta(days=MAX_AGE_DAYS).total_seconds()
    
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            # 检查文件年龄
            file_age = now - os.path.getctime(file_path)
            if file_age > max_age:
                try:
                    os.remove(file_path)
                    print(f"已删除过期文件: {filename}")
                except Exception as e:
                    print(f"删除文件失败 {filename}: {e}")

if __name__ == "__main__":
    cleanup_old_files() 