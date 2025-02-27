<template>
  <div class="article-card" @click="navigateToArticle">
    <div class="article-cover" v-if="article.cover_image">
      <img :src="getImageUrl(article.cover_image)" :alt="article.title" />
    </div>
    <div class="article-content">
      <div class="article-meta">
        <span class="article-date">{{ formatDate(article.created_at) }}</span>
        <span class="article-category" v-if="article.category">
          <el-tag size="small" effect="plain">{{ article.category.name }}</el-tag>
        </span>
      </div>
      <h3 class="article-title">{{ article.title }}</h3>
      <p class="article-excerpt">{{ getExcerpt(article.content) }}</p>
      <div class="article-footer">
        <span class="article-views">
          <el-icon><View /></el-icon> {{ article.views_count }}
        </span>
        <span class="article-comments">
          <el-icon><ChatLineRound /></el-icon> {{ article.comments_count }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { View, ChatLineRound } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import axios from '../utils/axios'

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const router = useRouter()

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${axios.defaults.baseURL}${path}`
}

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

// 获取文章摘要
const getExcerpt = (content) => {
  if (!content) return ''
  
  // 移除HTML标签
  const plainText = content.replace(/<[^>]+>/g, '')
  
  // 截取前100个字符
  return plainText.length > 100 
    ? plainText.substring(0, 100) + '...' 
    : plainText
}

// 导航到文章详情页
const navigateToArticle = () => {
  router.push(`/article/${props.article.id}`)
}
</script>

<style scoped>
.article-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.article-cover {
  height: 180px;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.article-card:hover .article-cover img {
  transform: scale(1.05);
}

.article-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.article-date {
  font-size: 14px;
  color: #666;
}

.article-title {
  font-size: 18px;
  margin: 0 0 10px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-excerpt {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-footer {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #999;
}

.article-views, .article-comments {
  display: flex;
  align-items: center;
  gap: 5px;
}

@media (max-width: 768px) {
  .article-cover {
    height: 160px;
  }
  
  .article-content {
    padding: 15px;
  }
  
  .article-title {
    font-size: 16px;
  }
}
</style>