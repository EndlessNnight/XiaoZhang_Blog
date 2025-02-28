<template>
  <div class="movies-page-container">
    <!-- 使用头部组件，并传入 banner 相关属性 -->
    <site-header
      :show-banner="true"
      banner-title="影视分享"
      banner-subtitle="分享优质电影、电视剧"
      banner-color="linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d)"
    />

    <section class="movies-content">
      <div class="container">
        <div class="filter-section">
          <div class="category-tabs">
            <el-tabs v-model="activeTab" @tab-change="handleTabChange">
              <el-tab-pane label="全部" name="all"></el-tab-pane>
              <el-tab-pane label="电影" name="movie"></el-tab-pane>
              <el-tab-pane label="电视剧" name="tv"></el-tab-pane>
            </el-tabs>
          </div>
          
          <div class="sort-options">
            <el-select v-model="sortBy" placeholder="排序方式" @change="handleSortChange">
              <el-option label="观看日期 ↓" value="watch_date_desc"></el-option>
              <el-option label="观看日期 ↑" value="watch_date_asc"></el-option>
              <el-option label="评分 ↓" value="rating_desc"></el-option>
              <el-option label="发行日期 ↓" value="release_date_desc"></el-option>
            </el-select>
          </div>
        </div>
        
        <div class="movies-list-container">
          <el-skeleton v-if="loading" :rows="5" animated />
          
          <transition-group 
            v-else 
            name="fade" 
            tag="div"
            appear
          >
            <el-row :gutter="24" :key="activeTab + sortBy">
              <el-col 
                v-for="movie in filteredMovies" 
                :key="movie.id" 
                :xs="12" 
                :sm="8" 
                :md="6" 
                :lg="6" 
                :xl="6"
                class="movie-col"
              >
                <div 
                  class="movie-card" 
                  @click="showMovieDetail(movie)"
                >
                  <div class="movie-poster">
                    <img :src="getImageUrl(movie.poster_path)" :alt="movie.title" />
                    <div class="movie-overlay">
                      <div class="movie-overlay-content">
                        <h3 class="movie-title">{{ movie.title }}</h3>
                        <p class="movie-year">{{ getYear(movie.release_date) }}</p>
                        <div class="movie-genres-mini">
                          <template v-if="getGenresArray(movie.genres).length > 0">
                            <el-tag 
                              v-for="genre in getGenresArray(movie.genres).slice(0, 4)" 
                              :key="genre"
                              size="small"
                              effect="plain"
                              class="genre-tag-mini"
                            >
                              {{ genre }}
                            </el-tag>
                            <span v-if="getGenresArray(movie.genres).length > 4" class="more-genres">
                              +{{ getGenresArray(movie.genres).length - 4 }}
                            </span>
                          </template>
                          <span v-else class="no-genres">暂无标签</span>
                        </div>
                        <p class="movie-watched-date" v-if="movie.watch_date">
                          观看于: {{ formatWatchedDate(movie.watch_date) }}
                        </p>
                        <el-button class="view-detail-btn" size="small" round>查看详情</el-button>
                      </div>
                    </div>
                    <div class="movie-type-badge">{{ getMediaTypeText(movie.type) }}</div>
                    <div :class="['movie-rating-badge', { 'no-rating': !movie.rating }]">
                      <span v-if="movie.rating">{{ (movie.rating).toFixed(1) }}</span>
                      <span v-else>暂无</span>
                    </div>
                    <div class="movie-watched-badge" v-if="movie.watched">
                      <el-icon><Check /></el-icon>
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <el-empty 
              v-if="filteredMovies.length === 0" 
              :key="'empty'"
              description="暂无影视内容" 
              :image-size="200"
            ></el-empty>
          </transition-group>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container" v-if="totalMovies > 0">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalMovies"
            layout="prev, pager, next, jumper"
            @current-change="handlePageChange"
            background
          />
        </div>
      </div>
    </section>

    <!-- 电影详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="null"
      width="80%"
      destroy-on-close
      custom-class="movie-detail-dialog"
    >
      <div class="movie-detail" v-if="selectedMovie">
        <div class="movie-detail-header">
          <div class="movie-poster-large">
            <img :src="getImageUrl(selectedMovie.poster_path)" :alt="selectedMovie.title" />
            <div class="movie-rating-large-badge">
              {{ (selectedMovie.rating).toFixed(1) }}
            </div>
            <div class="movie-watched-large-badge" v-if="selectedMovie.watched">
              <el-icon><Check /></el-icon> 已观看
            </div>
          </div>
          <div class="movie-detail-info">
            <h2>{{ selectedMovie.title }}</h2>
            <p class="original-title" v-if="selectedMovie.original_title && selectedMovie.original_title !== selectedMovie.title">
              {{ selectedMovie.original_title }}
            </p>
            
            <div class="movie-genres">
              <template v-if="getGenresArray(selectedMovie.genres).length > 0">
                <el-tag 
                  v-for="genre in getGenresArray(selectedMovie.genres)" 
                  :key="genre"
                  size="small"
                  :type="getGenreType(genre)"
                  effect="light"
                  class="genre-tag"
                >
                  {{ genre }}
                </el-tag>
              </template>
              <span v-else class="no-genres-detail">暂无标签</span>
            </div>
            
            <div class="movie-meta-detail">
              <div class="meta-item">
                <span class="meta-label">类型</span>
                <span class="meta-value">{{ getMediaTypeText(selectedMovie.type) }}</span>
              </div>
              <div class="meta-item" v-if="selectedMovie.release_date">
                <span class="meta-label">发行日期</span>
                <span class="meta-value">{{ formatDate(selectedMovie.release_date) }}</span>
              </div>
              <div class="meta-item" v-if="selectedMovie.watch_date">
                <span class="meta-label">观看日期</span>
                <span class="meta-value">{{ formatDate(selectedMovie.watch_date) }}</span>
              </div>
              <div class="meta-item" v-if="selectedMovie.director">
                <span class="meta-label">导演</span>
                <span class="meta-value">{{ selectedMovie.director }}</span>
              </div>
              <div class="meta-item" v-if="selectedMovie.cast">
                <span class="meta-label">主演</span>
                <span class="meta-value">{{ selectedMovie.cast }}</span>
              </div>
              <div class="meta-item" v-if="selectedMovie.country">
                <span class="meta-label">国家/地区</span>
                <span class="meta-value">{{ selectedMovie.country }}</span>
              </div>
            </div>
            
            <div class="movie-external-links">
              <a 
                v-if="selectedMovie.tmdb_id" 
                :href="`https://www.themoviedb.org/${selectedMovie.type}/${selectedMovie.tmdb_id}`" 
                target="_blank"
                class="external-link tmdb-link"
              >
                <el-button size="small">
                  <el-icon><Link /></el-icon> TMDB
                </el-button>
              </a>
              <a 
                v-if="selectedMovie.imdb_id" 
                :href="`https://www.imdb.com/title/${selectedMovie.imdb_id}`" 
                target="_blank"
                class="external-link imdb-link"
              >
                <el-button size="small">
                  <el-icon><Link /></el-icon> IMDB
                </el-button>
              </a>
            </div>
          </div>
        </div>
        
        <div class="movie-overview-full" v-if="selectedMovie.overview">
          <h3>剧情简介</h3>
          <p>{{ selectedMovie.overview }}</p>
        </div>
        
        <div class="movie-trailer" v-if="selectedMovie.trailer_url">
          <h3>预告片</h3>
          <div class="trailer-container">
            <iframe 
              :src="getEmbedUrl(selectedMovie.trailer_url)" 
              frameborder="0" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
              allowfullscreen
            ></iframe>
          </div>
        </div>
        
        <div class="movie-notes" v-if="selectedMovie.notes">
          <h3>观后感</h3>
          <div class="notes-content">
            {{ selectedMovie.notes }}
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 使用尾部组件 -->
    <site-footer />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Link } from '@element-plus/icons-vue'
import axios from '../utils/axios'
import SiteHeader from '../components/SiteHeader.vue'
import SiteFooter from '../components/SiteFooter.vue'

const route = useRoute()

// 状态
const loading = ref(true)
const movies = ref([])
const totalMovies = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const dialogVisible = ref(false)
const selectedMovie = ref(null)
const activeTab = ref('all')
const sortBy = ref('watch_date_desc')

// 计算属性：根据当前标签过滤电影
const filteredMovies = computed(() => {
  if (activeTab.value === 'all') {
    return movies.value
  }
  return movies.value.filter(movie => movie.type === activeTab.value)
})

// 获取电影列表
const fetchMovies = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      skip: (page - 1) * pageSize.value,
      limit: pageSize.value,
      sort_by: sortBy.value
    }
    
    // 如果有选择类型，添加类型过滤
    if (activeTab.value !== 'all') {
      params.type = activeTab.value
    }
    
    const response = await axios.get('/v1/movies/', { params })
    movies.value = response.data.items || []
    totalMovies.value = response.data.total || 0
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('获取影视列表失败:', error)
    ElMessage.error('获取影视列表失败')
  } finally {
    loading.value = false
  }
}

// 处理页面变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchMovies(page)
}

// 处理标签变化
const handleTabChange = () => {
  currentPage.value = 1
  fetchMovies(1)
}

// 处理排序变化
const handleSortChange = () => {
  currentPage.value = 1
  fetchMovies(1)
}

// 显示电影详情
const showMovieDetail = (movie) => {
  selectedMovie.value = movie
  dialogVisible.value = true
}

// 获取媒体类型文本
const getMediaTypeText = (type) => {
  switch (type) {
    case 'movie':
      return '电影'
    case 'tv':
      return '电视剧'
    default:
      return '未知'
  }
}

// 获取年份
const getYear = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).getFullYear()
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

// 格式化观看日期（更简洁的格式）
const formatWatchedDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric'
  })
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${axios.defaults.baseURL}${path}`
}

// 将逗号分隔的类型字符串转换为数组
const getGenresArray = (genresString) => {
  if (!genresString) return []
  if (Array.isArray(genresString)) return genresString
  
  return genresString.split(',')
    .map(genre => genre.trim())
    .filter(genre => genre !== '')
}

// 获取嵌入式URL（用于视频）
const getEmbedUrl = (url) => {
  if (!url) return ''
  
  // YouTube
  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    const videoId = url.includes('v=') 
      ? url.split('v=')[1].split('&')[0]
      : url.split('/').pop()
    return `https://www.youtube.com/embed/${videoId}`
  }
  
  // Bilibili
  if (url.includes('bilibili.com')) {
    const bvid = url.includes('video/') 
      ? url.split('video/')[1].split('?')[0]
      : ''
    return `https://player.bilibili.com/player.html?bvid=${bvid}&high_quality=1&danmaku=0`
  }
  
  return url
}

// 根据类型获取标签颜色
const getGenreType = (genre) => {
  const genreMap = {
    '动作': 'danger',
    '冒险': 'warning',
    '喜剧': 'success',
    '剧情': 'info',
    '科幻': 'primary',
    '恐怖': 'danger',
    '爱情': 'danger',
    '动画': 'success',
    '奇幻': 'warning',
    '悬疑': 'info',
    '惊悚': 'danger',
    '犯罪': 'danger',
    '纪录片': 'info',
    '战争': 'danger',
    '历史': 'info',
    '音乐': 'success',
    '家庭': 'success',
    '传记': 'info'
  }
  
  return genreMap[genre] || ''
}

// 检查URL参数中是否有电影ID
const checkMovieIdInUrl = async () => {
  const movieId = route.query.id
  if (movieId) {
    try {
      const response = await axios.get(`/v1/movies/${movieId}`)
      showMovieDetail(response.data)
    } catch (error) {
      console.error('获取电影详情失败:', error)
    }
  }
}

// 监听排序方式变化
watch(sortBy, () => {
  currentPage.value = 1
  fetchMovies(1)
})

// 设置页面标题
onMounted(() => {
  document.title = '影视分享 - 小张博客'
  fetchMovies()
  checkMovieIdInUrl()
})

// 当显示电影详情时更新标题
watch(selectedMovie, (newMovie) => {
  if (newMovie) {
    document.title = `${newMovie.title} - 影视分享 - 小张博客`
  } else {
    document.title = '影视分享 - 小张博客'
  }
})
</script>

<style scoped>
/* 容器样式 */
.movies-page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 内容区域样式 */
.movies-content {
  padding: 40px 0;
  min-height: calc(100vh - 300px); /* 保持最小高度，防止内容区域高度跳动 */
}

/* 骨架屏样式 */
.movies-content :deep(.el-skeleton) {
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* 添加内容过渡效果 */
.fade-move,
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.fade-leave-active {
  position: absolute;
}

/* 修改电影列表容器样式 */
.movies-list-container {
  position: relative;
  min-height: 200px; /* 设置最小高度 */
}

/* 筛选区域样式 */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.category-tabs {
  flex: 1;
}

.category-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.category-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.category-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  padding: 0 24px;
  height: 40px;
  line-height: 40px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.category-tabs :deep(.el-tabs__item:hover) {
  color: #409eff;
}

.category-tabs :deep(.el-tabs__item.is-active) {
  font-weight: 600;
}

.category-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
}

.sort-options {
  width: 180px;
  margin-left: 20px;
}

.sort-options :deep(.el-input__wrapper) {
  border-radius: 20px;
  padding: 0 15px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.3s ease;
}

.sort-options :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.sort-options :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset !important;
}

.sort-options :deep(.el-select-dropdown__item) {
  padding: 0 15px;
  height: 36px;
  line-height: 36px;
}

/* 电影卡片样式 */
.movie-col {
  margin-bottom: 30px;
}

.movie-card {
  background-color: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.movie-poster {
  position: relative;
  overflow: hidden;
  padding-top: 150%; /* 2:3 比例 */
}

.movie-poster img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.05);
}

.movie-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.8) 100%);
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
  color: white;
  transform: translateY(5px);
}

.movie-card:hover .movie-overlay {
  opacity: 1;
  transform: translateY(0);
}

.movie-overlay-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.movie-overlay .movie-title {
  color: white;
  font-size: 20px;
  margin-bottom: 12px;
  line-height: 1.4;
  max-height: 56px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  width: 100%;
  font-weight: 600;
}

.movie-overlay .movie-year {
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 16px;
  font-size: 15px;
  font-weight: 500;
}

.movie-overlay .movie-genres-mini {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  justify-content: center;
  width: 100%;
}

.movie-overlay .genre-tag-mini {
  background-color: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: white !important;
  font-size: 12px !important;
  padding: 0 10px !important;
  height: 24px !important;
  line-height: 22px !important;
  backdrop-filter: blur(4px);
}

.movie-overlay .more-genres {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  background-color: rgba(255, 255, 255, 0.15);
  padding: 0 10px;
  border-radius: 12px;
  height: 24px;
  line-height: 24px;
  display: inline-block;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(4px);
}

.movie-overlay .no-genres {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0 10px;
  border-radius: 12px;
  height: 24px;
  line-height: 24px;
  display: inline-block;
  border: 1px dashed rgba(255, 255, 255, 0.3);
}

.movie-overlay .movie-watched-date {
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 20px;
  font-size: 15px;
  font-weight: 500;
}

.movie-overlay .view-detail-btn {
  width: 140px;
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
  height: 36px;
  font-size: 14px;
  font-weight: 500;
}

.movie-overlay .view-detail-btn:hover {
  background-color: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.movie-type-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  backdrop-filter: blur(4px);
  z-index: 1;
}

.movie-rating-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(243, 156, 18, 0.9);
  color: white;
  min-width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  backdrop-filter: blur(4px);
  z-index: 1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  padding: 0 6px;
}

.movie-rating-badge.no-rating {
  background-color: rgba(149, 165, 166, 0.9);
  font-size: 12px;
  font-weight: normal;
}

.movie-watched-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(39, 174, 96, 0.9);
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  z-index: 1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

/* 修改电影信息区域的样式 */
.movie-info {
  display: none; /* 隐藏原来的信息区域 */
}

.movie-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 8px;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  /* -webkit-line-clamp: 2; */
  -webkit-box-orient: vertical;
  line-height: 1.4;
  height: 48px;
}

.movie-year {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0 0 8px;
}

.movie-genres-mini {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.genre-tag-mini {
  font-size: 11px !important;
  padding: 0 6px !important;
  height: 22px !important;
  line-height: 20px !important;
}

.more-genres {
  font-size: 11px;
  color: #666;
  background-color: #f0f0f0;
  padding: 0 6px;
  border-radius: 11px;
  height: 22px;
  line-height: 22px;
  display: inline-block;
}

.no-genres {
  font-size: 11px;
  color: #999;
  background-color: #f5f5f5;
  padding: 0 8px;
  border-radius: 11px;
  height: 22px;
  line-height: 22px;
  display: inline-block;
  border: 1px dashed #ddd;
}

.movie-watched-date {
  font-size: 13px;
  color: #666;
  margin: 0;
  margin-top: auto;
  padding-top: 8px;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding: 20px 0;
}

/* 影视详情样式 */
.movie-detail-dialog :deep(.el-dialog__header) {
  display: none;
}

.movie-detail-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.movie-detail {
  padding: 30px;
  background-color: #fff;
}

.movie-detail-header {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.movie-poster-large {
  width: 280px;
  flex-shrink: 0;
  position: relative;
}

.movie-poster-large img {
  width: 100%;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.movie-rating-large-badge {
  position: absolute;
  top: -15px;
  right: -15px;
  background-color: #f39c12;
  color: white;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.movie-watched-large-badge {
  position: absolute;
  bottom: -10px;
  right: -10px;
  background-color: #27ae60;
  color: white;
  padding: 6px 12px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.movie-detail-info {
  flex: 1;
}

.movie-detail-info h2 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 32px;
  color: #2c3e50;
}

.original-title {
  color: #666;
  margin-bottom: 20px;
  font-style: italic;
  font-size: 16px;
}

.movie-meta-detail {
  margin-bottom: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 18px;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-weight: bold;
  color: #7f8c8d;
  margin-bottom: 6px;
  font-size: 15px;
}

.meta-value {
  color: #2c3e50;
  font-size: 16px;
}

.movie-genres {
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.genre-tag {
  margin-right: 0;
  font-size: 14px !important;
}

.movie-external-links {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.external-link {
  text-decoration: none;
}

.movie-overview-full {
  margin-bottom: 36px;
  background-color: #f8f9fa;
  padding: 24px;
  border-radius: 10px;
}

.movie-overview-full h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 22px;
  color: #2c3e50;
}

.movie-overview-full p {
  line-height: 1.8;
  color: #34495e;
  margin: 0;
  font-size: 16px;
}

.movie-notes {
  margin-top: 36px;
  background-color: #fff8e1;
  padding: 24px;
  border-radius: 10px;
  border-left: 5px solid #ffc107;
}

.movie-notes h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 22px;
  color: #2c3e50;
}

.notes-content {
  line-height: 1.8;
  color: #34495e;
  white-space: pre-line;
  font-size: 16px;
}

.movie-trailer {
  margin-top: 36px;
}

.movie-trailer h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 22px;
  color: #2c3e50;
}

.trailer-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 比例 */
  height: 0;
  overflow: hidden;
  border-radius: 10px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.trailer-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.no-genres-detail {
  font-size: 15px;
  color: #999;
  background-color: #f5f5f5;
  padding: 6px 14px;
  border-radius: 5px;
  display: inline-block;
  border: 1px dashed #ddd;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .movie-detail-header {
    flex-direction: column;
  }
  
  .movie-poster-large {
    width: 100%;
    max-width: 320px;
    margin: 0 auto 24px;
  }
  
  .movie-meta-detail {
    grid-template-columns: 1fr;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
    padding: 15px;
  }
  
  .sort-options {
    margin-top: 15px;
    width: 100%;
    margin-left: 0;
  }
  
  .category-tabs :deep(.el-tabs__item) {
    padding: 0 15px;
    font-size: 14px;
  }
  
  .movie-title {
    font-size: 16px;
    height: 44px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .movie-title {
    font-size: 16px;
  }
}
</style>