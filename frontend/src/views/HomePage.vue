<template>
  <div class="home-page-container">
    <!-- 使用头部组件，并传入 banner 相关属性 -->
    <site-header
      :show-banner="true"
      banner-title="欢迎来到小张的博客"
      banner-subtitle="分享技术、生活和有趣的故事"
      banner-color="linear-gradient(to right, #3494e6, #ec6ead)"
    >
      <!-- <template #banner-content>
        <div class="banner-search">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文章..."
            prefix-icon="Search"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
      </template> -->
    </site-header>

    <!-- 主要内容区域 -->
    <main class="home-content">
      <div class="container">
        <!-- 最新文章区域 -->
        <section class="latest-articles">
          <h2 class="section-title">最新文章</h2>
          
          <el-skeleton v-if="loading" :rows="5" animated />
          
          <div v-else class="articles-grid">
            <article-card
              v-for="article in latestArticles"
              :key="article.id"
              :article="article"
            />
          </div>
          
          <div class="view-more">
            <router-link to="/articles" class="view-more-link">
              查看更多文章 <el-icon><ArrowRight /></el-icon>
            </router-link>
          </div>
        </section>
        
        <!-- 分类区域 -->
        <section class="categories-section" id="categories">
          <h2 class="section-title">文章分类</h2>
          
          <el-skeleton v-if="loading" :rows="3" animated />
          
          <div v-else class="categories-grid">
            <div
              v-for="category in categories"
              :key="category.id"
              class="category-card"
              @click="navigateToCategory(category.id)"
            >
              <div class="category-icon">
                <el-icon :size="32"><Folder /></el-icon>
              </div>
              <h3 class="category-name">{{ category.name }}</h3>
              <p class="category-count">{{ category.articles_count || 0 }} 篇文章</p>
            </div>
          </div>
        </section>
        
        <!-- 关于我区域 -->
        <section class="about-section" id="about">
          <h2 class="section-title">关于我</h2>
          
          <div class="about-content">
            <div class="about-image">
              <img src="https://via.placeholder.com/300x300" alt="小张的头像" />
            </div>
            <div class="about-text">
              <h3>你好，我是小张</h3>
              <p>
                我是一名全栈开发者，热爱编程和技术分享。这个博客是我记录学习心得、分享技术见解的地方。
              </p>
              <p>
                我擅长的技术栈包括 Vue.js、Python、FastAPI 等。平时喜欢研究新技术，也喜欢看电影、听音乐。
              </p>
              <p>
                如果你有任何问题或者想要交流，欢迎通过以下方式联系我：
              </p>
              <div class="social-links">
                <a href="mailto:example@example.com" title="Email">
                  <el-icon :size="24"><Message /></el-icon>
                </a>
                <a href="https://github.com/" target="_blank" title="GitHub">
                  <el-icon :size="24"><Link /></el-icon>
                </a>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
    
    <!-- 使用尾部组件 -->
    <site-footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Folder, Message, Link } from '@element-plus/icons-vue'
import axios from '../utils/axios'
import SiteHeader from '../components/SiteHeader.vue'
import SiteFooter from '../components/SiteFooter.vue'
import ArticleCard from '../components/ArticleCard.vue'

const router = useRouter()
const loading = ref(true)
const latestArticles = ref([])
const categories = ref([])
// const searchQuery = ref('')

// 获取最新文章
const fetchLatestArticles = async () => {
  try {
    const response = await axios.get('/v1/articles/', {
      params: {
        skip: 0,
        limit: 6
      }
    })
    latestArticles.value = response.data.items
  } catch (error) {
    console.error('获取最新文章失败:', error)
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

// // 处理搜索
// const handleSearch = () => {
//   if (searchQuery.value.trim()) {
//     router.push({
//       path: '/search',
//       query: { q: searchQuery.value.trim() }
//     })
//   }
// }

// 导航到分类页面
const navigateToCategory = (categoryId) => {
  router.push({
    path: '/articles',
    query: { category: categoryId }
  })
}

// 组件挂载时获取数据
onMounted(async () => {
  try {
    await Promise.all([
      fetchLatestArticles(),
      fetchCategories()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Banner 搜索框 */
.banner-search {
  margin-top: 20px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

/* 内容区域 */
.home-content {
  padding: 40px 0;
}

/* 通用部分样式 */
.section-title {
  font-size: 28px;
  margin-bottom: 30px;
  position: relative;
  padding-bottom: 10px;
  color: #333;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background-color: #409eff;
}

/* 最新文章区域 */
.latest-articles {
  margin-bottom: 60px;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.view-more {
  margin-top: 30px;
  text-align: center;
}

.view-more-link {
  display: inline-flex;
  align-items: center;
  color: #409eff;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s;
}

.view-more-link:hover {
  color: #66b1ff;
  transform: translateX(5px);
}

.view-more-link .el-icon {
  margin-left: 5px;
  transition: transform 0.3s;
}

.view-more-link:hover .el-icon {
  transform: translateX(3px);
}

/* 分类区域 */
.categories-section {
  margin-bottom: 60px;
  padding-top: 20px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.category-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  cursor: pointer;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.category-icon {
  margin-bottom: 15px;
  color: #409eff;
}

.category-name {
  font-size: 18px;
  margin: 0 0 10px;
  color: #333;
}

.category-count {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 关于我区域 */
.about-section {
  margin-bottom: 60px;
  padding-top: 20px;
}

.about-content {
  display: flex;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.about-image {
  flex: 0 0 300px;
}

.about-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.about-text {
  flex: 1;
  padding: 30px;
}

.about-text h3 {
  font-size: 24px;
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.about-text p {
  font-size: 16px;
  line-height: 1.6;
  color: #666;
  margin-bottom: 15px;
}

.social-links {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.social-links a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f5f7fa;
  color: #409eff;
  transition: all 0.3s;
}

.social-links a:hover {
  background-color: #409eff;
  color: #fff;
  transform: translateY(-3px);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .about-content {
    flex-direction: column;
  }
  
  .about-image {
    flex: 0 0 auto;
    height: 200px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
  }
}
</style>