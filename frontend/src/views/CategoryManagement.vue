<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>分类管理</span>
        <el-button type="primary" @click="showCreateDialog">新建分类</el-button>
      </div>
    </template>
    
    <el-table
      :data="categories"
      style="width: 100%"
      border
      stripe
      :default-sort="{ prop: 'created_at', order: 'descending' }"
    >
      <el-table-column prop="name" label="分类名称" sortable />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" sortable width="180">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button-group>
            <el-button size="default" type="primary" @click="showEditDialog(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              size="default" 
              type="danger" 
              @click="handleDelete(scope.row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 分类表单对话框 -->
  <el-dialog
    :title="dialogTitle"
    v-model="dialogVisible"
    width="500px"
    destroy-on-close
  >
    <el-form 
      :model="categoryForm"
      :rules="rules"
      ref="categoryFormRef"
      label-width="100px"
      status-icon
    >
      <el-form-item label="分类名称" prop="name">
        <el-input v-model="categoryForm.name" maxlength="50" show-word-limit />
      </el-form-item>
      <el-form-item label="描述">
        <el-input 
          v-model="categoryForm.description"
          type="textarea"
          :rows="3"
          maxlength="200"
          show-word-limit
          placeholder="请输入分类描述（选填）"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import axios from '../utils/axios'

const categories = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingCategoryId = ref(null)

const categoryForm = ref({
  name: '',
  description: ''
})

const categoryFormRef = ref(null)

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await axios.get('/v1/categories/')
    categories.value = response.data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

// 显示创建分类对话框
const showCreateDialog = () => {
  dialogTitle.value = '新建分类'
  categoryForm.value = {
    name: '',
    description: ''
  }
  editingCategoryId.value = null
  dialogVisible.value = true
}

// 显示编辑分类对话框
const showEditDialog = (category) => {
  dialogTitle.value = '编辑分类'
  categoryForm.value = {
    name: category.name,
    description: category.description
  }
  editingCategoryId.value = category.id
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!categoryFormRef.value) return
  
  try {
    await categoryFormRef.value.validate()
    
    if (editingCategoryId.value) {
      await axios.put(`/v1/categories/${editingCategoryId.value}`, categoryForm.value)
      ElMessage.success('更新分类成功')
    } else {
      await axios.post('/categories/', categoryForm.value)
      ElMessage.success('创建分类成功')
    }
    
    dialogVisible.value = false
    fetchCategories()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 删除分类
const handleDelete = async (category) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该分类吗？如果分类下有文章将无法删除。',
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    await axios.delete(`/v1/categories/${category.id}`)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (error) {
    if (error === 'cancel') return
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-button-group {
  display: flex;
  gap: 8px;
}
</style> 