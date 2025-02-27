<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '200px'" class="aside">
      <div class="logo" :class="{ 'collapsed': isCollapse }">
        <h2>{{ isCollapse ? 'XZ' : 'XiaoZhangBlog' }}</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        :collapse="isCollapse"
        :router="true"
        background-color="#2b3a4d"
        text-color="#bfcbd9"
        active-text-color="#fff"
      >
        <el-sub-menu index="1">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="2">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>内容管理</span>
          </template>
          <el-menu-item index="/admin/articles">
            <el-icon><Document /></el-icon>
            <template #title>文章管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/categories">
            <el-icon><Collection /></el-icon>
            <template #title>文章分类</template>
          </el-menu-item>
          <el-menu-item index="/admin/movies">
            <el-icon><VideoCamera /></el-icon>
            <template #title>影视管理</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon 
            class="collapse-btn"
            @click="toggleCollapse"
          >
            <Fold v-if="!isCollapse"/>
            <Expand v-else/>
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPath }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              <el-avatar 
                :size="32" 
                :src="currentUserAvatar" 
                :icon="UserFilled"
              />
              <span class="username">{{ username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  User, 
  Document, 
  Collection, 
  UserFilled,
  Setting,
  Fold,
  Expand,
  VideoCamera
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from '../utils/axios'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const username = ref('管理员')
const currentUserAvatar = ref('')

// 获取当前用户信息
const getCurrentUser = async () => {
  try {
    const response = await axios.get('/v1/users/me')
    username.value = response.data.username
    currentUserAvatar.value = response.data.avatar ? 
      `${axios.defaults.baseURL}${response.data.avatar}` : ''
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const activeMenu = computed(() => route.path)

const currentPath = computed(() => {
  const pathMap = {
    '/users': '用户管理',
    '/articles': '内容管理  /  文章管理',
    '/categories': '内容管理  /  文章分类',
    '/movies': '内容管理  /  影视管理'
  }
  return pathMap[route.path] || '首页'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    router.push('/login')
    ElMessage.success('已退出登录')
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  getCurrentUser()
})

// 切换菜单折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// const handleOpen = (key, keyPath) => {
//   console.log('打开菜单:', key, keyPath)
// }

// const handleClose = (key, keyPath) => {
//   console.log('关闭菜单:', key, keyPath)
// }
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f5f7f9;
}

.aside {
  background: #2b3a4d;
  transition: width 0.3s;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.15);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo.collapsed {
  padding: 0 10px;
}

.logo h2 {
  color: #fff;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.3s;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.collapse-btn {
  padding: 8px;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s;
  margin-right: 16px;
  color: #606266;
  border-radius: 4px;
}

.collapse-btn:hover {
  color: #667eea;
  background-color: rgba(102, 126, 234, 0.1);
}

/* 菜单样式 */
:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  margin: 4px 0;
  border-radius: 4px;
  margin: 4px 8px;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-menu--collapse) {
  width: 64px;
}

/* 头部样式 */
.header {
  background-color: #fff;
  border-bottom: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  height: 60px;
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.el-dropdown-link:hover {
  background: rgba(102, 126, 234, 0.1);
}

.username {
  margin-left: 8px;
  color: #606266;
  font-weight: 500;
}

/* 头像样式 */
:deep(.el-avatar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 面包屑样式 */
:deep(.el-breadcrumb__inner) {
  color: #606266;
  font-weight: 500;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #667eea;
  font-weight: 600;
}

/* 主内容区域 */
.el-main {
  background-color: #f5f7f9;
  padding: 20px;
}

/* 添加过渡动画 */
.el-aside,
.el-menu-vertical,
.el-menu-item,
.el-sub-menu,
.logo {
  transition: all 0.3s cubic-bezier(.645,.045,.355,1);
}

/* 卡片样式 */
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border: none;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}
</style> 