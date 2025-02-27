import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import LoginPage from '../views/LoginPage.vue'
import UserManagement from '../views/UserManagement.vue'
import ArticleManagement from '../views/ArticleManagement.vue'
import CategoryManagement from '../views/CategoryManagement.vue'
import MovieManagement from '../views/MovieManagement.vue'
import HomePage from '../views/HomePage.vue'
import ArticleDetail from '../views/ArticleDetail.vue'
import MoviesPage from '../views/MoviesPage.vue'
import axios from '../utils/axios'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    component: HomePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/article/:id',
    component: ArticleDetail,
    meta: { requiresAuth: false }
  },
  {
    path: '/movies',
    component: MoviesPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    component: AppLayout,
    children: [
      {
        path: '',
        redirect: '/admin/users'
      },
      {
        path: 'users',
        name: 'Users',
        component: UserManagement,
        meta: { requiresAuth: true }
      },
      {
        path: 'articles',
        name: 'Articles',
        component: ArticleManagement,
        meta: { requiresAuth: true }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: CategoryManagement,
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'movies',
        name: 'MovieManagement',
        component: MovieManagement,
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 验证 token 是否有效，并检查是否为管理员
const validateToken = async () => {
  try {
    const response = await axios.get('/v1/users/me')
    return response.data.is_admin // 返回是否为管理员
  } catch (error) {
    return false
  }
}

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth) {
    if (!token) {
      ElMessage.error('请先登录')
      next('/login')
      return
    }
    
    // 验证 token 有效性和管理员权限
    const isAdmin = await validateToken()
    if (!isAdmin) {
      localStorage.removeItem('token')
      ElMessage.error('需要管理员权限')
      next('/login')
      return
    }
  } else if (to.path === '/login' && token) {
    const isAdmin = await validateToken()
    if (isAdmin) {
      next('/admin/users')
      return
    }
  }
  
  next()
})

export default router 