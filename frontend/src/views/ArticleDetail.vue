<template>
  <div class="article-detail-container">
    <!-- 使用头部组件，不显示 banner -->
    <site-header
      :show-banner="true"
      banner-title="欢迎来到小张的博客"
      banner-subtitle="分享技术、生活和有趣的故事"
      banner-color="linear-gradient(to right, #3494e6, #ec6ead)"
    />

    <section class="article-content">
      <div class="container">
      <div class="article-content-wrapper">
        <el-skeleton v-if="loading" :rows="15" animated />
        
        <template v-else>
          <div class="article-header">
            <h1 class="article-title">{{ article.title }}</h1>
            <div class="article-meta">
              <span class="category" v-if="article.category">
                <el-tag size="small" effect="dark">{{ article.category.name }}</el-tag>
              </span>
              <span class="date">{{ formatDate(article.created_at) }}</span>
              <span class="views"><el-icon><View /></el-icon> {{ article.views_count }}</span>
              <span class="comments"><el-icon><ChatLineRound /></el-icon> {{ article.comments_count }}</span>
            </div>
          </div>
          
          <div class="article-cover" v-if="article.cover_image">
            <img :src="getImageUrl(article.cover_image)" alt="文章封面" />
          </div>
          
          <div class="article-content" v-html="article.content"></div>
          
          <div class="article-actions">
            <el-button type="primary" plain @click="handleLike">
              <el-icon><Star /></el-icon> 点赞 ({{ article.likes_count }})
            </el-button>
            <el-button @click="scrollToComments">
              <el-icon><ChatLineRound /></el-icon> 评论 ({{ article.comments_count }})
            </el-button>
          </div>
          
          <div class="article-comments" id="comments">
            <h3>评论区 ({{ article.comments_count }})</h3>
            
            <div class="comment-form">
              <el-input
                v-model="commentContent"
                type="textarea"
                :rows="4"
                placeholder="写下你的评论..."
                :maxlength="500"
                show-word-limit
              />
              <div class="comment-form-actions">
                <el-button type="primary" @click="submitComment" :loading="submitting">
                  发表评论
                </el-button>
              </div>
            </div>
            
            <div class="comments-list">
              <template v-if="article.comments && article.comments.length > 0">
                <comment-item
                  v-for="comment in article.comments"
                  :key="comment.id"
                  :comment="comment"
                  :current-user="currentUser"
                  :article-id="article.id"
                  @refresh="fetchArticle"
                />
              </template>
              <el-empty v-else description="暂无评论，快来发表第一条评论吧！" />
            </div>
          </div>
        </template>
      </div>
      
      <aside class="article-sidebar">
        <div class="sidebar-section">
          <h3>相关文章</h3>
          <el-skeleton v-if="loading" :rows="5" animated />
          <ul v-else class="related-articles">
            <li v-for="relatedArticle in relatedArticles" :key="relatedArticle.id">
              <router-link :to="`/article/${relatedArticle.id}`">
                {{ relatedArticle.title }}
              </router-link>
            </li>
          </ul>
        </div>
        
        <div class="sidebar-section">
          <h3>文章分类</h3>
          <el-skeleton v-if="loading" :rows="3" animated />
          <div v-else class="categories-list">
            <el-tag
              v-for="category in categories"
              :key="category.id"
              class="category-tag"
              effect="plain"
            >
              {{ category.name }}
            </el-tag>
          </div>
        </div>
      </aside>
    </div>
    </section>
    
    
    <!-- 使用尾部组件 -->
    <site-footer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, ChatLineRound, Star } from '@element-plus/icons-vue'
import axios from '../utils/axios'
import CommentItem from '../components/CommentItem.vue'
import SiteHeader from '../components/SiteHeader.vue'
import SiteFooter from '../components/SiteFooter.vue'

const route = useRoute()
const router = useRouter()
const articleId = ref(parseInt(route.params.id))

const loading = ref(true)
const submitting = ref(false)
const article = ref({})
const relatedArticles = ref([])
const categories = ref([])
const commentContent = ref('')
const currentUser = ref(null)

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${axios.defaults.baseURL}${path}`
}

// 获取相关文章
const fetchRelatedArticles = async () => {
  try {
    // 获取同分类的其他文章
    const categoryId = article.value.category?.id
    if (categoryId) {
      const response = await axios.get('/v1/articles/', {
        params: {
          skip: 0,
          limit: 5,
          category_id: categoryId
        }
      })
      
      // 过滤掉当前文章
      relatedArticles.value = response.data
        .filter(a => a.id !== article.value.id)
        .slice(0, 5)
    }
  } catch (error) {
    console.error('获取相关文章失败:', error)
  }
}

// 获取文章详情
const fetchArticle = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/v1/articles/${articleId.value}`)
    article.value = response.data
    
    // 更新页面标题
    document.title = `${article.value.title} - 小张博客`
    
    // 获取相关文章
    fetchRelatedArticles()
    await fetchComments()
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('获取文章详情失败')
    router.push('/')
  } finally {
    loading.value = false
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

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      const response = await axios.get('/v1/users/me')
      currentUser.value = response.data
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 获取评论列表
const fetchComments = async () => {
  try {
    const response = await axios.get(`/v1/comments/${article.value.id}`)
    article.value.comments = response.data
  } catch (error) {
    console.error('获取评论失败:', error)
  }
}

// 提交评论
const submitComment = async () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  
  if (!currentUser.value) {
    ElMessage.warning('请先登录后再评论')
    // 保存当前页面路径，登录后返回
    localStorage.setItem('redirectPath', window.location.pathname)
    router.push('/login')
    return
  }
  
  try {
    submitting.value = true
    await axios.post('/v1/comments/', {
      content: commentContent.value,
      article_id: articleId.value,
      parent_id: null // 顶级评论
    })
    
    ElMessage.success('评论成功')
    commentContent.value = ''
    
    // 刷新文章数据
    fetchArticle()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '评论失败')
  } finally {
    submitting.value = false
  }
}

// 点赞文章
const handleLike = async () => {
  // if (!currentUser.value) {
  //   ElMessage.warning('请先登录后再点赞')
  //   router.push('/login')
  //   return
  // }
  
  try {
    await axios.put(`/v1/articles/${article.value.id}/like`)
    
    // 更新点赞数
    article.value.likes_count += 1
    ElMessage.success('点赞成功')
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

// 滚动到评论区
const scrollToComments = () => {
  document.getElementById('comments').scrollIntoView({ behavior: 'smooth' })
}

// 监听路由参数变化，重新获取文章
watch(() => route.params.id, (newId) => {
  if (newId && newId !== articleId.value) {
    articleId.value = parseInt(newId)
    fetchArticle()
  }
})

// 组件挂载时获取数据
onMounted(() => {
  fetchArticle()
  fetchCategories()
  fetchCurrentUser()
})
</script>

<style scoped>
.article-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  gap: 30px;
}

/* 站点头部 */
.site-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  margin-bottom: 30px;
}

.site-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  color: #333;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s;
}

.main-nav a:hover, .main-nav a.router-link-active {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

.admin-link {
  color: #409eff !important;
}

/* 文章内容区 */
.article-content-wrapper {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin-bottom: 30px;
}

.article-header {
  margin-bottom: 20px;
}

.article-title {
  font-size: 28px;
  margin: 0 0 15px;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #666;
  font-size: 14px;
}

.article-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.article-cover {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 30px;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.article-content :deep(h2) {
  margin-top: 30px;
  margin-bottom: 15px;
  font-size: 22px;
}

.article-content :deep(h3) {
  margin-top: 25px;
  margin-bottom: 10px;
  font-size: 20px;
}

.article-content :deep(p) {
  margin-bottom: 15px;
}

.article-content :deep(pre) {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 15px;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 15px;
  color: #666;
  margin: 0 0 15px;
}

.article-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

/* 评论区 */
.article-comments {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.article-comments h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 20px;
}

.comment-form {
  margin-bottom: 30px;
}

.comment-form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 侧边栏 */
.article-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.sidebar-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.sidebar-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.related-articles {
  list-style: none;
  padding: 0;
  margin: 0;
}

.related-articles li {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #eee;
}

.related-articles li:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.related-articles a {
  text-decoration: none;
  color: #333;
  transition: color 0.3s;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-articles a:hover {
  color: #409eff;
}

.categories-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-tag {
  cursor: pointer;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
  
  .article-sidebar {
    width: 100%;
  }
  
  .main-nav {
    display: none;
  }
}

.article-content {
  padding: 40px 0;
}
</style>