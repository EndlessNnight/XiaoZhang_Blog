-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS xiaozhangblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE xiaozhangblog;

-- 创建管理员用户（密码需要使用bcrypt加密）
INSERT INTO users (username, email, hashed_password, is_admin, created_at)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpwDM.qVLykFRK', -- 密码：admin123
    1,
    NOW()
);

-- 创建默认分类
INSERT INTO categories (name, description, created_at)
VALUES 
    ('技术', '技术相关文章', NOW()),
    ('生活', '生活随笔', NOW()),
    ('电影', '电影评论', NOW()); 