<template>
  <div class="site-header-wrapper">
    <header class="site-header">
      <div class="container">
        <div class="logo">
          <router-link to="/">
            <h1>XiaoZhangBlog</h1>
          </router-link>
        </div>
        <nav class="main-nav">
          <ul>
            <li><router-link :to="{ path: '/' }" :class="{ active: isActive('/') }">首页</router-link></li>
            <li><router-link :to="{ path: '/movies' }" :class="{ active: isActive('/movies') }">影视</router-link></li>
            <li><a href="/#categories">分类</a></li>
            <li><a href="/#about">关于</a></li>
            <li><router-link to="/admin" class="admin-link">管理后台</router-link></li>
          </ul>
        </nav>
        
        <!-- 移动端菜单按钮 -->
        <div class="mobile-menu-toggle" @click="toggleMobileMenu">
          <el-icon><Menu /></el-icon>
        </div>
      </div>
    </header>
    
    <!-- 移动端菜单 -->
    <div class="mobile-menu" :class="{ 'mobile-menu-active': mobileMenuActive }">
      <ul>
        <li><router-link :to="{ path: '/' }" @click="closeMobileMenu">首页</router-link></li>
        <li><router-link :to="{ path: '/movies' }" @click="closeMobileMenu">影视</router-link></li>
        <li><a href="/#categories" @click="closeMobileMenu">分类</a></li>
        <li><a href="/#about" @click="closeMobileMenu">关于</a></li>
        <li><router-link to="/admin" class="admin-link" @click="closeMobileMenu">管理后台</router-link></li>
      </ul>
    </div>
    
    <!-- 可复用的 Banner 组件 -->
    <div v-if="showBanner" class="page-banner" :style="bannerStyle">
      <div class="container">
        <h2>{{ bannerTitle }}</h2>
        <p v-if="bannerSubtitle">{{ bannerSubtitle }}</p>
        <slot name="banner-content"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps } from 'vue'
import { useRoute } from 'vue-router'
import { Menu } from '@element-plus/icons-vue'

const props = defineProps({
  showBanner: {
    type: Boolean,
    default: false
  },
  bannerTitle: {
    type: String,
    default: ''
  },
  bannerSubtitle: {
    type: String,
    default: ''
  },
  bannerImage: {
    type: String,
    default: ''
  },
  bannerColor: {
    type: String,
    default: 'linear-gradient(135deg, #3494e6, #ec6ead)'
  }
})

const route = useRoute()
const mobileMenuActive = ref(false)

// 判断当前路由是否激活
const isActive = (path) => {
  return route.path === path
}

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuActive.value = !mobileMenuActive.value
  
  // 当菜单打开时，禁止页面滚动
  if (mobileMenuActive.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  mobileMenuActive.value = false
  document.body.style.overflow = ''
}

// 计算 banner 样式
const bannerStyle = computed(() => {
  const style = {}
  
  if (props.bannerImage) {
    style.backgroundImage = `url(${props.bannerImage})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
  } else {
    style.background = props.bannerColor
  }
  
  return style
})
</script>

<style scoped>
.site-header-wrapper {
  position: relative;
}

.site-header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.site-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.logo a {
  text-decoration: none;
  color: inherit;
}

.main-nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 20px;
}

.main-nav a {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  padding: 5px 0;
  transition: color 0.3s;
}

.main-nav a:hover, .main-nav a.active {
  color: #409eff;
}

.admin-link {
  color: #409eff !important;
}

/* 移动端菜单按钮 */
.mobile-menu-toggle {
  display: none;
  cursor: pointer;
  font-size: 24px;
  color: #333;
}

/* 移动端菜单 */
.mobile-menu {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 99;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-menu-active {
  opacity: 1;
  visibility: visible;
}

.mobile-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: center;
}

.mobile-menu li {
  margin: 20px 0;
}

.mobile-menu a {
  text-decoration: none;
  color: white;
  font-size: 20px;
  font-weight: 500;
  transition: color 0.3s;
  padding: 10px 20px;
  display: block;
}

.mobile-menu a:hover {
  color: #409eff;
}

/* Banner 样式 */
.page-banner {
  color: white;
  padding: 60px 0;
  text-align: center;
}

.page-banner h2 {
  font-size: 36px;
  margin-bottom: 15px;
  margin-top: 0;
}

.page-banner p {
  font-size: 18px;
  max-width: 600px;
  margin: 0 auto;
  opacity: 0.9;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .main-nav {
    display: none;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .page-banner h2 {
    font-size: 28px;
  }
  
  .page-banner p {
    font-size: 16px;
  }
  
  .site-header {
    height: 60px;
  }
}
</style> 