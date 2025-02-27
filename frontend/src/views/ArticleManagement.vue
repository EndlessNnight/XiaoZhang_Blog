<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span>文章管理</span>
          <el-switch
            v-model="showHidden"
            class="ml-2"
            style="margin-left: 16px"
            inline-prompt
            :active-icon="View"
            :inactive-icon="Hide"
            active-text="显示隐藏文章"
            inactive-text="仅显示公开文章"
          />
        </div>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建文章
        </el-button>
      </div>
    </template>
    
    <el-table
      :data="articles"
      style="width: 100%"
      border
      :default-sort="{ prop: 'created_at', order: 'descending' }"
      :header-cell-style="{ 'text-align': 'center' }"
    >
      <el-table-column prop="category" label="分类" width="120">
        <template #default="scope">
          <el-tag
            :type="getCategoryTagType(scope.row.category?.name)"
            effect="light"
          >
            {{ scope.row.category?.name || '未分类' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="50" show-overflow-tooltip />
      <el-table-column label="封面图" width="120">
        <template #default="scope">
          <el-image 
            v-if="scope.row.cover_image"
            :src="getImageUrl(scope.row.cover_image)" 
            style="width: 100px; height: 60px"
            fit="cover"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column prop="views_count" label="阅读数" width="100" sortable />
      <el-table-column prop="likes_count" label="点赞数" width="100" sortable />
      <el-table-column prop="comments_count" label="评论数" width="100" sortable />
      <el-table-column prop="created_at" label="创建时间" sortable width="180">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="is_hidden" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_hidden ? 'info' : 'success'">
            {{ scope.row.is_hidden ? '已隐藏' : '已发布' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="200" fixed="right">
        <template #default="scope">
          <el-button-group>
            <el-button size="default" type="primary" @click="showEditDialog(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="default" type="danger" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
            <el-button 
              size="default" 
              :type="scope.row.is_hidden ? 'success' : 'warning'"
              @click="handleToggleVisibility(scope.row)"
            >
              <el-icon><Hide v-if="!scope.row.is_hidden" /><View v-else /></el-icon>
              {{ scope.row.is_hidden ? '显示' : '隐藏' }}
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 文章表单对话框 -->
  <el-dialog
    :title="dialogTitle"
    v-model="dialogVisible"
    width="50%"
    :before-close="handleClose"
    :destroy-on-close="true"
  >
    <el-form :model="articleForm" label-width="100px">
      <el-form-item label="标题">
        <el-input v-model="articleForm.title"></el-input>
      </el-form-item>
      <el-form-item label="封面图">
        <el-upload
          class="avatar-uploader"
          :action="`${axios.defaults.baseURL}/v1/upload/image`"
          :show-file-list="false"
          :on-success="handleCoverSuccess"
          :before-upload="beforeCoverUpload"
          :headers="uploadHeaders"
        >
          <img 
            v-if="articleForm.cover_image" 
            :src="getImageUrl(articleForm.cover_image)" 
            class="cover-image" 
          />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item label="正文">
        <div style="border: 1px solid #ccc">
          <Toolbar
            style="border-bottom: 1px solid #ccc"
            :editor="editorRef"
            :defaultConfig="toolbarConfig"
            mode="default"
          />
          <Editor
            style="height: 500px"
            v-model="articleForm.content"
            :defaultConfig="editorConfig"
            mode="default"
            @onCreated="handleCreated"
          />
        </div>
      </el-form-item>
      <el-form-item label="分类" prop="category_id">
        <el-select v-model="articleForm.category_id" placeholder="请选择分类">
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="评论列表" v-if="editingArticleId">
        <div class="comments-container">
          <!-- 添加评论输入框 -->
          <div class="add-comment-section">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="2"
              placeholder="写下你的评论..."
              :maxlength="500"
              show-word-limit
            />
            <el-button type="primary" @click="handleAddComment">
              <el-icon><ChatDotRound /></el-icon>
              发表评论
            </el-button>
          </div>

          <!-- 评论列表 -->
          <div class="comments-list" v-if="commentsTree.length > 0">
            <comment-item
              v-for="comment in commentsTree"
              :key="comment.id"
              :comment="comment"
              :current-user="currentUser"
              :article-id="editingArticleId"
              @refresh="fetchComments(editingArticleId)"
            />
          </div>
          
          <!-- 无评论时的提示 -->
          <el-empty 
            v-else 
            description="暂无评论" 
            :image-size="200"
          >
            <template #description>
              <p>还没有人评论，来说两句吧~</p>
            </template>
          </el-empty>
        </div>
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
import { ref, shallowRef, onMounted, computed, onBeforeUnmount, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import axios from '../utils/axios'
import { Plus, Edit, Delete, Picture, ChatDotRound, Hide, View } from '@element-plus/icons-vue'
import CommentItem from '../components/CommentItem.vue'

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

// 获取当前 token
const getToken = () => localStorage.getItem('token')

// 内容 HTML
const articleForm = ref({
  title: '',
  content: '',
  cover_image: '',
  author_id: null,
  category_id: null
})

// 编辑器配置
const toolbarConfig = {
  excludeKeys: [
    'uploadVideo',
    'insertTable',
    'group-video',
    'insertImage'
  ]
}

const editorConfig = { 
  placeholder: '请输入内容...',
  MENU_CONF: {
    uploadImage: {
      server: `${axios.defaults.baseURL}/v1/upload/image`,
      fieldName: 'file',
      maxFileSize: 2 * 1024 * 1024,
      maxNumberOfFiles: 10,
      allowedFileTypes: ['image/*'],
      headers: {
        Authorization: `Bearer ${getToken()}`
      },
      onBeforeUpload() {
        return true
      },
      onProgress: (progress) => {
        console.log('上传进度', progress)
      },
      onSuccess: (_, res) => {
        console.log('上传成功', res)
        ElMessage.success('图片上传成功')
        return `${axios.defaults.baseURL}${res.url}`
      },
      onFailed: (_, res) => {
        console.log('上传失败', res)
        ElMessage.error('图片上传失败')
        return false
      },
      onError: (_, err, res) => {
        console.log('上传出错', err, res)
        ElMessage.error(`图片上传出错: ${err.message}`)
        return false
      },
      customInsert(res, insertFn) {
        const fullUrl = `${axios.defaults.baseURL}${res.url}`
        insertFn(fullUrl)
      }
    }
  }
}

// 在编辑器创建后的处理
const handleCreated = (editor) => {
  editorRef.value = editor
}

// 组件销毁时，销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

const articles = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingArticleId = ref(null)
const comments = ref([])
const newComment = ref('')
const currentUser = ref(null)
const categories = ref([])
const totalArticles = ref(0)

// 添加上传请求头的计算属性
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 添加显示隐藏文章的开关状态
const showHidden = ref(true)

// 获取文章列表
const fetchArticles = async () => {
  try {
    const response = await axios.get('/v1/articles/', {
      params: {
        include_hidden: showHidden.value
      }
    })
    articles.value = response.data.items || []
    totalArticles.value = response.data.total || 0
  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('获取文章列表失败')
  }
}

// 获取评论列表
const fetchComments = async (articleId) => {
  try {
    const response = await axios.get(`/v1/comments/${articleId}`)
    comments.value = response.data
  } catch (error) {
    console.error('获取评论失败:', error)
  }
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

// 显示创建文章对话框
const showCreateDialog = () => {
  dialogTitle.value = '新建文章'
  articleForm.value = {
    title: '',
    content: '',
    cover_image: '',
    author_id: currentUser.value?.id,
    category_id: null
  }
  editingArticleId.value = null
  dialogVisible.value = true
}

// 显示编辑文章对话框
const showEditDialog = async (article) => {
  dialogTitle.value = '编辑文章'
  const content = article.content.replace(
    /src="\/uploads\//g, 
    `src="${axios.defaults.baseURL}/uploads/`
  )
  
  articleForm.value = {
    title: article.title,
    content: content,
    cover_image: article.cover_image,
    author_id: article.author_id,
    category_id: article.category_id
  }
  editingArticleId.value = article.id
  dialogVisible.value = true
  await fetchComments(article.id)
}

// 关闭对话框
const handleClose = () => {
  ElMessageBox.confirm('确认关闭？未保存的内容将会丢失', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    dialogVisible.value = false
  }).catch(() => {})
}

// 添加图片 URL 处理函数
const getImageUrl = (path) => {
  if (!path) return ''
  return `${axios.defaults.baseURL}${path}`
}

// 修改上传成功处理函数
const handleCoverSuccess = (res) => {
  articleForm.value.cover_image = res.url
}

const beforeCoverUpload = (file) => {
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

// 提交表单
const handleSubmit = async () => {
  try {
    // 构建提交数据
    const submitData = {
      title: articleForm.value.title,
      content: articleForm.value.content,
      cover_image: articleForm.value.cover_image,
      author_id: currentUser.value.id,  // 添加作者ID
      category_id: articleForm.value.category_id
    }

    if (editingArticleId.value) {
      await axios.put(`/v1/articles/${editingArticleId.value}`, submitData)
      ElMessage.success('更新文章成功')
    } else {
      await axios.post('/v1/articles/', submitData)
      ElMessage.success('创建文章成功')
    }
    dialogVisible.value = false
    fetchArticles()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 删除文章
const handleDelete = async (article) => {
  try {
    await ElMessageBox.confirm('确定要删除该文章吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`/v1/articles/${article.id}`)
    ElMessage.success('删除成功')
    fetchArticles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 将评论列表转换为树形结构
const commentsTree = computed(() => {
  if (!Array.isArray(comments.value)) return []
  
  return comments.value.map(comment => ({
    ...comment,
    replies: Array.isArray(comment.replies) ? comment.replies : []
  }))
})

// 获取当前用户信息
const getCurrentUser = async () => {
  try {
    const response = await axios.get('/v1/users/me')
    currentUser.value = response.data
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 获取分类标签类型
const getCategoryTagType = (categoryName) => {
  const types = {
    '日常': 'primary',
    '代码': 'success',
    '闲聊': 'warning',
    '学习': 'info',
    '技术': 'danger'
  }
  return types[categoryName] || ''
}

// 组件挂载时获取文章列表和评论
onMounted(async () => {
  await getCurrentUser()
  await fetchCategories()
  await fetchArticles()
})

// 添加评论
const handleAddComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  try {
    await axios.post('/v1/comments/', {
      content: newComment.value,
      article_id: editingArticleId.value
    })
    
    newComment.value = ''
    await fetchComments(editingArticleId.value)
    // await updateCommentsCount(editingArticleId.value)
    ElMessage.success('评论成功')
  } catch (error) {
    ElMessage.error('评论失败')
  }
}

const handleToggleVisibility = async (article) => {
  try {
    await axios.put(`/v1/articles/${article.id}/visibility`)
    await fetchArticles()
    ElMessage.success(`文章已${article.is_hidden ? '显示' : '隐藏'}`)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// const updateCommentsCount = async (articleId) => {
//   try {
//     await axios.put(`/v1/articles/${articleId}/update-comments-count`)
//     await fetchArticles()
//   } catch (error) {
//     console.error('更新评论数失败:', error)
//   }
// }

// 监听 showHidden 的变化
watch(showHidden, () => {
  fetchArticles()
})

</script>

<style src="@wangeditor/editor/dist/css/style.css"></style>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 178px;
  height: 178px;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.cover-image {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}

.add-comment {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.add-comment .el-input {
  flex: 1;
}

/* 编辑器样式优化 */
.w-e-text-container {
  min-height: 400px !important;
}

.w-e-toolbar {
  border-bottom: 1px solid #eee;
}

.w-e-bar-item button {
  padding: 5px 10px;
}

.w-e-bar-item button:hover {
  background-color: #f5f5f5;
}

.article-dialog {
  /* 设置对话框的最大宽度和边距 */
  max-width: 90vw;
  margin: 20px auto;
  border-radius: 8px; /* 圆角 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); /* 阴影效果 */
}

.article-dialog .el-dialog__header {
  background-color: #f5f5f5; /* 头部背景色 */
  border-bottom: 1px solid #e4e7ed; /* 底部边框 */
  padding: 15px 20px; /* 内边距 */
  border-top-left-radius: 8px; /* 圆角 */
  border-top-right-radius: 8px; /* 圆角 */
}

.article-dialog .el-dialog__body {
  padding: 20px; /* 内边距 */
  background-color: #ffffff; /* 背景色 */
}

.article-dialog .el-dialog__footer {
  padding: 10px 20px; /* 内边距 */
  background-color: #f5f5f5; /* 底部背景色 */
  border-top: 1px solid #e4e7ed; /* 顶部边框 */
}

.article-dialog .el-button {
  border-radius: 4px; /* 按钮圆角 */
}

.article-dialog .el-button--primary {
  background-color: #409eff; /* 主按钮背景色 */
  border-color: #409eff; /* 主按钮边框色 */
}

.article-dialog .el-button--primary:hover {
  background-color: #66b1ff; /* 主按钮悬停色 */
}

.article-dialog .el-button--danger {
  background-color: #f56c6c; /* 危险按钮背景色 */
  border-color: #f56c6c; /* 危险按钮边框色 */
}

.article-dialog .el-button--danger:hover {
  background-color: #f78989; /* 危险按钮悬停色 */
}

.image-error {
  width: 100px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  color: #909399;
}

.el-button-group {
  display: flex;
  gap: 8px;
}

.el-tag {
  width: 100%;
  text-align: center;
}

.comments-container {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.add-comment-section {
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.add-comment-section .el-input {
  flex: 1;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-card {
  margin-bottom: 0;
  transition: all 0.3s;
}

.comment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.comment-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.time {
  color: #999;
  font-size: 12px;
}

.comment-content {
  color: #666;
  line-height: 1.6;
  font-size: 14px;
  padding: 8px 0;
}

.reply-input {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin: 8px 0;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.replies-section {
  margin-top: 16px;
  padding-left: 24px;
  border-left: 2px solid #ebeef5;
  background: rgba(0, 0, 0, 0.01);
  border-radius: 0 8px 8px 0;
}

.reply-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
  position: relative;
}

.reply-item:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 12px;
  padding-bottom: 12px;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reply-content {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  padding-left: 44px;
  margin-bottom: 8px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-button--link) {
  padding: 4px 8px;
  height: auto;
}

:deep(.el-button--link .el-icon) {
  margin-right: 4px;
}

/* 嵌套回复的输入框样式 */
.reply-input.nested {
  margin-top: 12px;
  margin-left: 44px;
  background: #fff;
  border-radius: 4px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 状态标签样式 */
.status-tag {
  min-width: 80px;
  text-align: center;
}

/* 开关样式 */
:deep(.el-switch) {
  margin-left: 16px;
}

:deep(.el-switch__label) {
  color: #666;
}

:deep(.el-switch.is-checked .el-switch__label) {
  color: #409eff;
}
</style> 