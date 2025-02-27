<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <div class="logo-title">
          <h2>XiaoZhangBlog</h2>
          <p>小张的博客后台管理</p>
        </div>
      </div>
      <div class="login-form">
        <div class="login-header">
          <h2>登录</h2>
          <p>欢迎回来！</p>
        </div>
        <el-form 
          :model="loginForm" 
          :rules="rules"
          ref="loginFormRef"
          class="login-form-body"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username"
              :prefix-icon="User"
              placeholder="请输入用户名"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password"
              type="password"
              :prefix-icon="Lock"
              placeholder="请输入密码"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-button" 
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import axios from '../utils/axios'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)
const loginForm = ref({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 检查登录状态
const checkLoginStatus = async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.get('/v1/users/me')
      router.push('/users')
    } catch (error) {
      localStorage.removeItem('token')
    }
  }
}

const handleLogin = async () => {
  if (loading.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const params = new URLSearchParams()
    params.append('username', loginForm.value.username)
    params.append('password', loginForm.value.password)

    const response = await axios.post('/v1/users/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    localStorage.setItem('token', response.data.access_token)
    ElMessage.success('登录成功')
    
    // 检查是否有重定向路径
    const redirectPath = localStorage.getItem('redirectPath')
    if (redirectPath) {
      localStorage.removeItem('redirectPath') // 清除重定向路径
      router.push(redirectPath)
    } else {
      // 如果没有重定向路径，则跳转到管理页面
      router.push('/admin/users')
    }
  } catch (error) {
    if (error.response) {
      if (error.response.status === 401) {
        ElMessage.error('用户名或密码错误，或没有管理员权限')
      } else {
        ElMessage.error(error.response?.data?.detail || '登录失败')
      }
    }
  } finally {
    loading.value = false
  }
}

// 组件挂载时检查登录状态
onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #3494e6, #ec6ead);
  overflow: hidden;
}

.login-box {
  display: flex;
  width: 900px;
  height: 500px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
}

.login-left {
  flex: 1;
  background: linear-gradient(45deg, #3494e6, #ec6ead);
  border-radius: 7px 0 0 7px;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.logo-title {
  text-align: center;
}

.logo-title h2 {
  font-size: 36px;
  margin-bottom: 10px;
}

.logo-title p {
  font-size: 16px;
  opacity: 0.8;
}

.login-form {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.login-header p {
  color: #999;
  font-size: 14px;
}

.login-form-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-form-body :deep(.el-input) {
  height: 40px;
}

.login-form-body :deep(.el-input__wrapper) {
  background-color: #f5f7fa;
  box-shadow: none;
  border: 1px solid #e4e7ed;
}

.login-form-body :deep(.el-input__wrapper:hover) {
  border-color: #409eff;
}

.login-button {
  width: 100%;
  height: 40px;
  border-radius: 20px;
  font-size: 16px;
  letter-spacing: 2px;
  background: linear-gradient(45deg, #3494e6, #ec6ead);
  border: none;
}

.login-button:hover {
  background: linear-gradient(45deg, #2c7bc7, #d85c97);
}

@media screen and (max-width: 768px) {
  .login-box {
    width: 90%;
    flex-direction: column;
    height: auto;
  }
  
  .login-left {
    border-radius: 10px 10px 0 0;
    padding: 20px;
  }
  
  .login-form {
    padding: 20px;
  }
}
</style> 