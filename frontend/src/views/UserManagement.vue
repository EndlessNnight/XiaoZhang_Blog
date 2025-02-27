<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>用户管理</span>
        <el-button type="primary" @click="showCreateDialog">新建用户</el-button>
      </div>
    </template>
    
    <el-table :data="users" style="width: 100%">
      <el-table-column prop="avatar" label="头像" width="100">
        <template #default="scope">
          <el-avatar
            v-if="scope.row.avatar"
            :size="40"
            :src="getImageUrl(scope.row.avatar)"
            fit="cover"
          />
          <el-avatar v-else :size="40" :icon="UserFilled" />
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="is_admin" label="角色">
        <template #default="scope">
          {{ scope.row.is_admin ? '管理员' : '普通用户' }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="default" type="primary" @click="showEditDialog(scope.row)"><el-icon><Edit /></el-icon>编辑</el-button>
          <el-button size="default" type="danger" @click="handleDelete(scope.row)"><el-icon><Delete /></el-icon>删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 用户表单对话框 -->
  <el-dialog
    :title="dialogTitle"
    v-model="dialogVisible"
    width="500px"
  >
    <el-form 
      :model="userForm" 
      :rules="rules"
      ref="userFormRef"
      label-width="100px"
    >
      <el-form-item label="头像">
        <el-upload
          class="avatar-uploader"
          :action="`${axios.defaults.baseURL}/v1/upload/image`"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
          :headers="uploadHeaders"
        >
          <el-avatar
            v-if="userForm.avatar"
            :size="50"
            :src="getImageUrl(userForm.avatar)"
            fit="cover"
          />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="userForm.username"></el-input>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="userForm.email">
          <template #append v-if="showVerificationButton">
            <el-button 
              :disabled="cooldown > 0"
              @click="sendVerificationCode"
            >
              {{ cooldown > 0 ? `${cooldown}s` : '获取验证码' }}
            </el-button>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item 
        label="验证码" 
        prop="verificationCode"
        v-if="showVerificationCode"
      >
        <el-input v-model="userForm.verificationCode" maxlength="6" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="userForm.password" type="password"></el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword" v-if="userForm.password">
        <el-input v-model="userForm.confirmPassword" type="password"></el-input>
      </el-form-item>
      <el-form-item label="角色">
        <el-switch
          v-model="userForm.is_admin"
          active-text="管理员"
          inactive-text="普通用户"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UserFilled, Edit, Delete } from '@element-plus/icons-vue'
import axios from '../utils/axios'
import { useRouter } from 'vue-router'

const users = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const userForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  is_admin: false,
  avatar: '',
  verificationCode: ''
})
const editingUserId = ref(null)
const userFormRef = ref(null)
const router = useRouter()
const originalEmail = ref('')
const cooldown = ref(0)
const showVerificationCode = ref(false)

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await axios.get('/v1/users/')
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 显示创建用户对话框
const showCreateDialog = () => {
  dialogTitle.value = '新建用户'
  userForm.value = {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    is_admin: false,
    avatar: '',
    verificationCode: ''
  }
  originalEmail.value = ''
  showVerificationCode.value = false
  editingUserId.value = null
  dialogVisible.value = true
}

// 显示编辑用户对话框
const showEditDialog = (user) => {
  dialogTitle.value = '编辑用户'
  userForm.value = {
    username: user.username,
    email: user.email,
    password: '',
    confirmPassword: '',
    is_admin: user.is_admin,
    avatar: user.avatar,
    verificationCode: ''
  }
  originalEmail.value = user.email
  showVerificationCode.value = false
  editingUserId.value = user.id
  dialogVisible.value = true
}

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur', validator: (rule, value, callback) => {
      if (!editingUserId.value && !value) {
        callback(new Error('请输入密码'))
      } else {
        callback()
      }
    }}
  ],
  confirmPassword: [
    { validator: (rule, value, callback) => {
      if (userForm.value.password && value !== userForm.value.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }, trigger: ['blur', 'change'] }
  ]
}

// 是否显示获取验证码按钮
const showVerificationButton = computed(() => {
  if (editingUserId.value) {
    return userForm.value.email !== originalEmail.value
  }
  return !!userForm.value.email
})

// 发送验证码
const sendVerificationCode = async () => {
  try {
    if (!userForm.value.email) {
      ElMessage.error('请输入邮箱地址')
      return
    }
    
    await axios.post('/v1/users/send-verification', {}, {
      params: {
        email: userForm.value.email
      }
    })
    
    ElMessage.success('验证码已发送')
    showVerificationCode.value = true
    cooldown.value = 60
    const timer = setInterval(() => {
      cooldown.value--
      if (cooldown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送验证码失败')
  }
}

// 修改提交表单函数
const handleSubmit = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    
    // 检查密码确认
    if (userForm.value.password && userForm.value.password !== userForm.value.confirmPassword) {
      ElMessage.error('两次输入的密码不一致')
      return
    }
    
    const submitData = {
      username: userForm.value.username,
      email: userForm.value.email,
      password: userForm.value.password,
      is_admin: userForm.value.is_admin,
      avatar: userForm.value.avatar
    }

    if (!editingUserId.value || userForm.value.email !== originalEmail.value) {
      if (!userForm.value.verificationCode) {
        ElMessage.error('请输入验证码')
        return
      }
      submitData.verificationCode = userForm.value.verificationCode
    }

    let response
    if (editingUserId.value) {
      response = await axios.put(`/v1/users/${editingUserId.value}`, submitData)
      ElMessage.success('更新用户成功')
      
      if (response.data.need_relogin) {
        ElMessage.warning('您修改了关键信息，需要重新登录')
        localStorage.removeItem('token')
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      }
    } else {
      response = await axios.post('/v1/users/', submitData)
      ElMessage.success('创建用户成功')
    }
    
    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 关闭对话框前重置表单
const handleClose = () => {
  userFormRef.value?.resetFields()
  dialogVisible.value = false
}

// 删除用户
const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      user.is_admin ? 
        '确定要删除该管理员用户吗？' : 
        '确定要删除该用户吗？', 
      '提示', 
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    await axios.delete(`/v1/users/${user.id}`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error === 'cancel') return
    
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 获取头像 URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${axios.defaults.baseURL}${path}`
}
// 头像上传成功处理
const handleAvatarSuccess = (res) => {
  userForm.value.avatar = res.url // 更新头像 URL
}

// 头像上传前的验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
  }
  return isImage && isLt2M
}

// 添加上传头像所需的 headers
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-uploader {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-uploader :deep(.el-avatar) {
  width: 50px;
  height: 50px;
}

/* 表格中的头像样式 */
.el-table :deep(.el-avatar) {
  display: block;
  margin: 0 auto;
}
</style> 
