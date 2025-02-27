# 小张博客系统

一个使用 FastAPI 和 Vue.js 构建的现代化博客系统。

## 功能特点

### 用户系统
- 用户注册/登录
- 邮箱验证
- 头像上传
- 用户角色管理（管理员/普通用户）

### 文章管理
- 文章的 CRUD 操作
- Markdown 编辑器
- 文章分类
- 文章封面图片
- 阅读量统计
- 文章评论系统
- 文章可见性控制（公开/隐藏）

### 评论系统
- 多级评论支持
- 评论的软删除
- 评论数统计
- 评论权限控制

### 分类管理
- 分类的 CRUD 操作
- 文章分类统计

### 电影管理
- 电影信息管理
- TMDB API 集成
- 电影封面和背景图片

### 文件上传
- 图片上传支持
- 文件类型验证
- 文件大小限制

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- MySQL
- JWT 认证
- 邮件服务
- TMDB API 集成

### 前端
- Vue 3
- Element Plus
- Vue Router
- Axios
- Wang Editor（富文本编辑器）

## 项目结构
```bash
├── backend/                # 后端项目根目录
│   ├── alembic/           # 数据库迁移配置
│   ├── app/               # 应用主目录
│   │   ├── api/          # API 路由层
│   │   │   └── v1/       # API v1 版本
│   │   │       ├── articles.py    # 文章相关接口
│   │   │       ├── auth.py        # 认证相关接口
│   │   │       ├── categories.py  # 分类相关接口
│   │   │       ├── comments.py    # 评论相关接口
│   │   │       ├── movies.py      # 电影相关接口
│   │   │       ├── upload.py      # 文件上传接口
│   │   │       └── users.py       # 用户相关接口
│   │   ├── core/         # 核心配置
│   │   │   ├── auth.py   # JWT认证
│   │   │   ├── config.py # 应用配置
│   │   │   ├── database.py # 数据库配置
│   │   │   └── email.py  # 邮件服务
│   │   ├── crud/         # 数据库操作层
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic模型
│   │   └── utils/        # 工具函数
│   ├── uploads/          # 文件上传目录
│   ├── main.py           # 应用入口
│   └── requirements.txt  # 依赖清单
└── frontend/             # 前端项目根目录
     ├── public/           # 静态资源
     ├── src/              # 源代码目录
     │   ├── assets/       # 资源文件
     │   ├── components/   # 通用组件
     │   │   ├── ArticleCard.vue    # 文章卡片组件
     │   │   ├── CommentItem.vue    # 评论项组件
     │   │   ├── SiteHeader.vue     # 网站头部组件
     │   │   └── SiteFooter.vue     # 网站底部组件
     │   ├── views/        # 页面组件
     │   │   ├── ArticleDetail.vue  # 文章详情页
     │   │   ├── ArticleManagement.vue # 文章管理页
     │   │   ├── CategoryManagement.vue # 分类管理页
     │   │   ├── HomePage.vue       # 首页
     │   │   ├── Login.vue         # 登录页
     │   │   ├── MovieManagement.vue # 电影管理页
     │   │   ├── Register.vue      # 注册页
     │   │   └── UserManagement.vue # 用户管理页
     │   ├── utils/        # 工具函数
     │   │   ├── axios.js  # axios配置
     │   │   └── auth.js   # 认证相关
     │   ├── router/       # 路由配置
     │   ├── App.vue       # 根组件
     │   └── main.js       # 应用入口
     ├── .env              # 环境变量
     ├── package.json      # 项目配置
     └── vite.config.js    # Vite配置
```

## 安装和运行

### 使用 Docker 部署

1. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填写必要的配置信息
```

2. 构建和启动服务：
```bash
docker-compose up -d
```

3. 执行数据库迁移：
```bash
docker-compose exec backend alembic upgrade head
```

访问：
- 前端：http://localhost
- 后端API：http://localhost/v1
- API文档：http://localhost/docs

### 后端

1. 安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填写必要的配置信息
```

3. 运行数据库迁移：
```bash
alembic upgrade head
```

4. 启动服务器：
```bash
uvicorn main:app --reload
```

### 前端

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置后端 API 地址
```

3. 启动开发服务器：
```bash
npm run dev
```

## API 文档

启动后端服务器后，访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

[MIT License](LICENSE)

