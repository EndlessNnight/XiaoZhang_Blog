from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.config import settings
from app.api import router as api_router
import uvicorn

app = FastAPI(
    title="XiaoZhangBlog API",
    description="小张博客的后端API",
    version="1.0.0"
)

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 允许的前端源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 创建上传目录
uploads_dir = os.path.join(os.getcwd(), settings.UPLOAD_DIR)
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 包含API路由
app.include_router(api_router)

# 导入路由
from app.api.v1 import users, articles, categories, comments, movies


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 