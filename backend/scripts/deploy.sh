#!/bin/bash

# 停止并删除旧容器
docker-compose down

# 拉取最新代码
git pull

# 复制生产环境配置
cp .env.prod .env

# 构建新镜像
docker-compose build

# 启动服务
docker-compose up -d

# 执行数据库迁移
docker-compose exec web python scripts/db.py upgrade

# 检查服务状态
docker-compose ps 