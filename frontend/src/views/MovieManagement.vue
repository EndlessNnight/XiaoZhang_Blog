<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <h2 class="title">影视管理</h2>
          <el-radio-group 
            v-model="viewMode" 
            size="small"
            style="margin-left: 16px;"
          >
            <el-radio-button value="card">
              卡片视图
            </el-radio-button>
            <el-radio-button value="timeline">
              时间线
            </el-radio-button>
          </el-radio-group>
          <el-input
            v-model="localSearch"
            placeholder="搜索影视..."
            class="header-search"
            @input="handleLocalSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select 
            v-if="viewMode === 'card'"
            v-model="sortBy" 
            placeholder="排序方式" 
            size="small"
            style="margin-left: 16px; width: 140px;"
          >
            <el-option label="评分从高到低" value="rating_desc" />
            <el-option label="评分从低到高" value="rating_asc" />
            <el-option label="上映日期最新" value="release_date_desc" />
            <el-option label="上映日期最早" value="release_date_asc" />
            <el-option label="观看日期最近" value="watch_date_desc" />
            <el-option label="观看日期最早" value="watch_date_asc" />
          </el-select>
        </div>
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加影视
        </el-button>
      </div>
    </template>

    <!-- 修改筛选器部分，仅在卡片视图显示 -->
    <div v-if="viewMode === 'card'" class="filters-section">
      <div class="filters-header">
        <h3>筛选条件</h3>
      </div>
      <div class="filters-content">
        <div class="filter-group">
          <h4>类型</h4>
          <el-select 
            v-model="filters.type" 
            placeholder="影视类型" 
            clearable
            popper-class="filter-select-dropdown"
          >
            <el-option label="电影" value="movie" />
            <el-option label="电视剧" value="tv" />
          </el-select>
        </div>

        <div class="filter-group">
          <h4>观看状态</h4>
          <el-select v-model="filters.watchStatus" placeholder="观看状态" clearable>
            <el-option label="已看" value="watched" />
            <el-option label="在看" value="watching" />
            <el-option label="想看" value="want_to_watch" />
          </el-select>
        </div>

        <div class="filter-group">
          <h4>最低评分</h4>
          <el-select 
            v-model="filters.rating" 
            placeholder="最低评分" 
            clearable
            popper-class="filter-select-dropdown"
          >
            <el-option :value="0" label="全部" />
            <el-option 
              v-for="rating in [1, 2, 3, 4, 5]" 
              :key="rating" 
              :value="rating" 
              :label="`${rating}星及以上`"
            >
              <template #default>
                <el-rate 
                  :model-value="rating" 
                  disabled 
                  show-score
                />
              </template>
            </el-option>
          </el-select>
        </div>
      </div>
    </div>

    <!-- 卡片视图 -->
    <div v-if="viewMode === 'card'" class="movie-grid">
      <el-card 
        v-for="movie in movies" 
        :key="movie.id" 
        class="movie-card"
        :body-style="{ padding: '0px' }"
        @click="handleEdit(movie)"
      >
        <div class="movie-poster-wrapper">
          <el-image
            :src="movie.poster_path"
            fit="cover"
            class="movie-poster"
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <!-- 观看状态图标 -->
          <div class="watch-status-icon" :class="getWatchStatusClass(movie.watch_status)">
            <el-icon>
              <Check v-if="movie.watch_status === 'watched'" />
              <VideoPlay v-else-if="movie.watch_status === 'watching'" />
              <Clock v-else-if="movie.watch_status === 'want_to_watch'" />
            </el-icon>
            <span class="status-text">
              {{ getWatchStatusText(movie.watch_status) }}
            </span>
          </div>
          <!-- 信息浮层 -->
          <div class="movie-info-overlay">
            <div class="movie-info">
              <h3 class="movie-title" :title="movie.title">{{ movie.title }}</h3>
              <div class="movie-meta">
                <el-tag size="small" :type="movie.type === 'movie' ? 'success' : 'warning'">
                  {{ movie.type === 'movie' ? '电影' : '剧集' }}
                </el-tag>
                <el-tag 
                  v-if="movie.release_date" 
                  size="small" 
                  type="info"
                >
                  {{ movie.release_date }}
                </el-tag>
              </div>
              <div class="movie-rating">
                <template v-if="movie.rating > 0">
                  <el-rate
                    v-model="movie.rating"
                    disabled
                    show-score
                    text-color="#ff9900"
                    :score-template="movie.rating.toFixed(1)"
                    :allow-half="true"
                  />
                </template>
                <span v-else class="no-rating">暂未评分</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 添加时间线视图 -->
    <div v-if="viewMode === 'timeline'" class="timeline-view">
      <el-timeline>
        <el-timeline-item
          v-for="movie in watchedMovies"
          :key="movie.id"
          :timestamp="formatDate(movie.watch_date)"
          placement="top"
          :type="getTimelineItemType(movie)"
        >
          <el-card class="timeline-card">
            <div class="timeline-content">
              <el-image
                :src="movie.poster_path"
                class="timeline-poster"
                fit="cover"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="timeline-info">
                <h3 class="timeline-title">{{ movie.title }}</h3>
                <p class="timeline-original-title">{{ movie.original_title }}</p>
                <div class="timeline-meta">
                  <el-tag size="small" :type="movie.type === 'movie' ? 'success' : 'warning'">
                    {{ movie.type === 'movie' ? '电影' : '剧集' }}
                  </el-tag>
                  <el-tag 
                    v-if="movie.release_date" 
                    size="small" 
                    type="info"
                  >
                    {{ movie.release_date }}
                  </el-tag>
                </div>
                <div class="timeline-rating">
                  <template v-if="movie.rating > 0">
                    <el-rate
                      v-model="movie.rating"
                      disabled
                      show-score
                      text-color="#ff9900"
                      :score-template="movie.rating.toFixed(1)"
                      :allow-half="true"
                    />
                  </template>
                  <span v-else class="no-rating">暂未评分</span>
                </div>
                <p class="timeline-overview">{{ movie.overview }}</p>
                <div class="timeline-actions">
                  <el-button 
                    type="primary" 
                    link
                    size="small"
                    @click="openTMDB(movie)"
                  >
                    <el-icon><Link /></el-icon>
                    前往 TMDB
                  </el-button>
                  <el-button 
                    type="primary" 
                    link
                    size="small"
                    @click="handleEdit(movie)"
                  >
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 修改分页组件 -->
    <div v-if="viewMode === 'card'"  class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 修改添加/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="50%"
    >
      <div v-if="!movieForm.id">
        <el-steps 
          :active="activeStep" 
          finish-status="success"
          class="dialog-steps"
        >
          <el-step title="选择类型" />
          <el-step title="搜索影视" />
          <el-step title="选择结果" />
          <el-step title="观看信息" />
        </el-steps>

        <div class="step-content">
          <!-- 步骤1：选择类型 -->
          <div v-if="activeStep === 0" class="step-type">
            <h3>请选择要添加的影视类型</h3>
            <div class="type-options">
              <el-card
                class="type-option"
                :class="{ 'is-selected': searchType === 'movie' }"
                @click="selectType('movie')"
              >
                <el-icon><VideoCamera /></el-icon>
                <span>电影</span>
              </el-card>
              <el-card
                class="type-option"
                :class="{ 'is-selected': searchType === 'tv' }"
                @click="selectType('tv')"
              >
                <el-icon><Monitor /></el-icon>
                <span>电视剧</span>
              </el-card>
            </div>
          </div>

          <!-- 步骤2：搜索 -->
          <div v-if="activeStep === 1" class="step-search">
            <h3>请输入影视名称</h3>
            <el-input
              v-model="searchQuery"
              placeholder="输入影视名称搜索..."
              @keyup.enter="handleSearchClick"
              :disabled="isSearching"
            >
              <template #append>
                <el-button 
                  type="primary" 
                  @click="handleSearchClick"
                  :loading="isSearching"
                >
                  <el-icon v-if="!isSearching"><Search /></el-icon>
                  {{ isSearching ? '搜索中...' : '搜索' }}
                </el-button>
              </template>
            </el-input>
            <div v-if="isSearching" class="search-loading">
              <el-skeleton :rows="3" animated />
            </div>
          </div>

          <!-- 步骤3：选择结果 -->
          <div v-if="activeStep === 2" class="step-results">
            <h3>请选择匹配的影视</h3>
            <el-scrollbar height="400px">
              <div class="search-results">
                <div
                  v-for="result in searchResults"
                  :key="result.tmdb_id"
                  class="search-result-item"
                  :class="{ 'is-selected': selectedMovie?.tmdb_id === result.tmdb_id }"
                  @click="selectResult(result)"
                >
                  <el-image
                    :src="result.poster_path"
                    :preview-src-list="[result.poster_path]"
                    fit="cover"
                    class="result-poster"
                  >
                    <template #error>
                      <div class="image-placeholder">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <div class="result-info">
                    <h4 class="result-title">{{ result.title }}</h4>
                    <p class="result-original-title">{{ result.original_title }}</p>
                    <p class="result-date">{{ result.release_date }}</p>
                    <p class="result-overview">{{ result.overview }}</p>
                  </div>
                </div>
              </div>
            </el-scrollbar>
          </div>

          <!-- 步骤4：观看信息 -->
          <div v-if="activeStep === 3" class="step-watch-info">
            <h3>请填写观看信息</h3>
            <el-form :model="movieForm" label-width="100px">
              <el-form-item label="观看状态">
                <el-select v-model="movieForm.watch_status" placeholder="请选择观看状态">
                  <el-option label="已看" value="watched" />
                  <el-option label="在看" value="watching" />
                  <el-option label="想看" value="want_to_watch" />
                </el-select>
              </el-form-item>
              <el-form-item label="观看日期" v-if="movieForm.watch_status === 'watched'">
                <el-date-picker
                  v-model="movieForm.watch_date"
                  type="date"
                  placeholder="选择日期"
                />
              </el-form-item>
              <el-form-item label="评分" v-if="movieForm.watch_status === 'watched'">
                <el-rate
                  v-model="movieForm.rating"
                  :allow-half="true"
                  show-score
                  text-color="#ff9900"
                  :score-template="movieForm.rating ? movieForm.rating.toFixed(1) : '0.0'"
                />
              </el-form-item>
              <el-form-item label="观看备注">
                <el-input
                  v-model="movieForm.comment"
                  type="textarea"
                  :rows="4"
                  placeholder="写下你的观看感受..."
                />
              </el-form-item>
            </el-form>
          </div>
        </div>

        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button 
            v-if="activeStep > 0" 
            @click="prevStep"
          >上一步</el-button>
          <el-button 
            v-if="activeStep < 3" 
            type="primary" 
            @click="nextStep"
            :disabled="!canGoNext"
          >下一步</el-button>
          <el-button 
            v-if="activeStep === 3" 
            type="primary" 
            @click="handleSubmit"
          >确定</el-button>
        </div>
      </div>

      <div v-else>
        <el-form :model="movieForm" label-width="100px">
          <!-- 影视信息展示 -->
          <div class="movie-detail">
            <div class="movie-detail-header">
              <el-image
                :src="movieForm.poster_path"
                fit="cover"
                class="detail-poster"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="detail-info">
                <h2 class="detail-title">{{ movieForm.title }}</h2>
                <p class="detail-original-title">{{ movieForm.original_title }}</p>
                <p v-if="movieForm.release_date" class="detail-date">
                  上映日期：{{ movieForm.release_date }}
                </p>
                <div class="detail-tags">
                  <el-tag size="small" :type="movieForm.type === 'movie' ? 'success' : 'warning'">
                    {{ movieForm.type === 'movie' ? '电影' : '剧集' }}
                  </el-tag>
                </div>
                <p class="detail-overview">{{ movieForm.overview }}</p>
                <div class="detail-actions">
                  <el-button 
                    type="primary" 
                    link
                    @click="openTMDB(movieForm)"
                  >
                    <el-icon><Link /></el-icon>
                    前往 TMDB
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 个人观看信息 -->
          <div class="watch-info">
            <h3 class="watch-info-title">个人观看信息</h3>
            <el-form-item label="观看状态">
              <el-select v-model="movieForm.watch_status">
                <el-option label="已看" value="watched" />
                <el-option label="在看" value="watching" />
                <el-option label="想看" value="want_to_watch" />
              </el-select>
            </el-form-item>

            <el-form-item label="评分">
              <el-rate
                v-model="movieForm.rating"
                :allow-half="true"
                show-score
                text-color="#ff9900"
                :score-template="movieForm.rating ? movieForm.rating.toFixed(1) : '0.0'"
              />
            </el-form-item>

            <el-form-item label="短评">
              <el-input
                v-model="movieForm.comment"
                type="textarea"
                :rows="3"
                maxlength="140"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="观看日期">
              <el-date-picker
                v-model="movieForm.watch_date"
                type="date"
                placeholder="选择日期"
              />
            </el-form-item>
          </div>
        </el-form>

        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="handleDelete(movieForm)"
          >删除</el-button>
          <el-button 
            type="primary" 
            @click="handleSubmit"
          >确定</el-button>
        </div>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Picture, 
  Check,  // 已看
  VideoPlay,  // 在看
  Clock,  // 想看
  Link,  // 添加链接图标
  Edit,     // 添加编辑图标
  VideoCamera,
  Monitor,
  Search
} from '@element-plus/icons-vue'
import axios from '../utils/axios'
import { debounce } from 'lodash'

// 初始化响应式数据
const viewMode = ref('card')
const movies = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加影视')
const searchQuery = ref('')
const searchResults = ref([])
const searchType = ref('movie')
const sortBy = ref('rating_desc') // 默认按评分从高到低排序


// 初始化表单数据
const movieForm = ref({
  tmdb_id: null,
  title: '',
  original_title: '',
  poster_path: '',
  backdrop_path: '',
  overview: '',
  release_date: null,
  type: 'movie',
  sub_type: '',
  genres: '',
  watch_status: 'want_to_watch',
  rating: 0,
  comment: '',
  watch_date: null
})

// 初始化筛选条件
const filters = ref({
  type: null,
  watchStatus: null,
  rating: null  // 改为 null，以支持清除选择
})

// 添加步骤相关的状态
const activeStep = ref(0)
const canGoNext = computed(() => {
  switch (activeStep.value) {
    case 0:
      return !!searchType.value
    case 1:
      return !!searchQuery.value
    case 2:
      return !!selectedMovie.value
    case 3:
      return true
    default:
      return false
  }
})

// 添加 selectedMovie 的定义
const selectedMovie = ref(null)

// 添加本地搜索相关的响应式数据
const localSearch = ref('')
const isSearching = ref(false)

// 添加计算每行可显示的卡片数量
const calculateCardsPerRow = () => {
  const movieGrid = document.querySelector('.movie-grid')
  if (!movieGrid) return 4 // 默认值

  const gridWidth = movieGrid.offsetWidth
  const cardWidth = 200 // 卡片基础宽度
  const gap = 24 // 卡片间距
  
  return Math.floor((gridWidth + gap) / (cardWidth + gap))
}

// 计算分页选项
const getPageSizes = () => {
  const cardsPerRow = calculateCardsPerRow()
  return [
    cardsPerRow * 3,  // 3行
    cardsPerRow * 4,  // 4行
    cardsPerRow * 5,  // 5行
    cardsPerRow * 6   // 6行
  ]
}

// 分页相关的响应式数据
const currentPage = ref(1)
const pageSizes = ref(getPageSizes())
const pageSize = ref(pageSizes.value[1]) // 默认选择4行
const total = ref(0)

// 添加窗口大小变化监听
const handleResize = () => {
  const newPageSizes = getPageSizes()
  pageSizes.value = newPageSizes
  
  // 调整当前页大小到最接近的新选项
  const currentSize = pageSize.value
  const closestSize = newPageSizes.reduce((prev, curr) => {
    return Math.abs(curr - currentSize) < Math.abs(prev - currentSize) ? curr : prev
  })
  
  if (pageSize.value !== closestSize) {
    pageSize.value = closestSize
    fetchMovies() // 重新获取数据
  }
}

// 在组件挂载时添加监听器
onMounted(() => {
  handleResize() // 初始计算
  window.addEventListener('resize', handleResize)
  fetchMovies()
})

// 在组件卸载时移除监听器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 修改本地搜索处理函数
const handleLocalSearch = debounce(async (value) => {
  if (!value) {
    fetchMovies() // 清空搜索时恢复原始列表
    return
  }

  try {
    const response = await axios.get('/v1/movies/search', {
      params: {
        query: value,
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })

    if (response.data && typeof response.data === 'object') {
      movies.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      movies.value = []
      total.value = 0
    }

    if (movies.value.length === 0) {
      ElMessage.info('未找到相关影视')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败: ' + (error.response?.data?.detail || error.message))
  }
}, 300)

// 监听搜索关键词变化
watch(localSearch, (newValue) => {
  if (!newValue) {
    fetchMovies() // 当搜索框清空时，恢复原始列表
  }
})

// 获取影视列表
const fetchMovies = async () => {
  try {
    const params = {
      type: filters.value.type,
      watch_status: filters.value.watchStatus,
      min_rating: filters.value.rating,
      sort_by: sortBy.value
    }

    // 仅在卡片视图时添加分页参数
    if (viewMode.value === 'card') {
      params.skip = (currentPage.value - 1) * pageSize.value
      params.limit = pageSize.value
    }

    const response = await axios.get('/v1/movies/', { params })
    
    if (response.data && typeof response.data === 'object') {
      movies.value = response.data.items || []
      if (viewMode.value === 'card') {
        total.value = response.data.total || 0
      }
    } else {
      movies.value = []
      total.value = 0
    }

    if (movies.value.length === 0) {
      ElMessage.info('没有找到符合条件的影视')
    }
  } catch (error) {
    console.error('获取影视列表失败:', error)
    ElMessage.error('获取影视列表失败: ' + (error.response?.data?.detail || error.message))
    movies.value = []
    total.value = 0
  }
}

// 修改搜索处理函数，添加加载状态
const handleSearch = async () => {
  if (!searchQuery.value) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  isSearching.value = true
  try {
    const response = await axios.get(`/v1/movies/tmdb/search/${searchType.value}`, {
      params: { query: searchQuery.value }
    })
    if (response.data && Array.isArray(response.data)) {
      searchResults.value = response.data
      if (searchResults.value.length === 0) {
        ElMessage.info('未找到相关结果')
      } else {
        nextStep()
      }
    } else {
      ElMessage.error('搜索结果格式错误')
    }
  } catch (error) {
    console.error('TMDB搜索错误:', error)
    ElMessage.error('搜索失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    isSearching.value = false
  }
}

// 修改选择结果函数
const selectResult = (result) => {
  selectedMovie.value = result
  movieForm.value = {
    ...movieForm.value,
    tmdb_id: Number(result.tmdb_id),
    title: result.title || '',
    original_title: result.original_title || '',
    poster_path: result.poster_path || '',
    backdrop_path: result.backdrop_path || '',
    overview: result.overview || '',
    release_date: result.release_date || null,
    type: searchType.value,
    sub_type: '',
    watch_status: 'want_to_watch',
    rating: 0,
    comment: '',
    watch_date: null
  }
  // 选择结果后自动进入下一步
  nextStep()
}

// 显示添加对话框
const showAddDialog = () => {
  activeStep.value = 0
  searchType.value = ''
  searchQuery.value = ''
  searchResults.value = []
  selectedMovie.value = null
  movieForm.value = {
    watch_status: 'want_to_watch',
    rating: 0
  }
  dialogVisible.value = true
}

// 显示编辑对话框
const handleEdit = (movie) => {
  dialogTitle.value = '编辑影视'
  movieForm.value = { ...movie }
  dialogVisible.value = true
}

// 删除影视
const handleDelete = async (movie) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await axios.delete(`/v1/movies/${movie.id}`)
    ElMessage.success('删除成功')
    dialogVisible.value = false  // 关闭对话框
    fetchMovies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 修改提交表单函数
const handleSubmit = async () => {
  try {
    // 确保评分是数字类型，并保留一位小数
    if (movieForm.value.rating) {
      movieForm.value.rating = parseFloat(movieForm.value.rating.toFixed(1))
    }
    
    // 处理表单数据
    const formData = {
      ...movieForm.value,
      rating: Number(movieForm.value.rating),
      tmdb_id: Number(movieForm.value.tmdb_id),
      release_date: movieForm.value.release_date ? new Date(movieForm.value.release_date).toISOString().split('T')[0] : null,
      watch_date: movieForm.value.watch_date ? new Date(movieForm.value.watch_date).toISOString().split('T')[0] : null
    }

    if (movieForm.value.id) {
      await axios.put(`/v1/movies/${movieForm.value.id}`, formData)
      ElMessage.success('更新成功')
    } else {
      try {
        await axios.post('/v1/movies/', formData)
        ElMessage.success('添加成功')
      } catch (error) {
        if (error.response?.status === 400) {
          // 如果是已存在的影视，显示特定的错误信息
          ElMessage.warning(error.response.data.detail || '该影视已存在')
          return
        }
        throw error  // 其他错误继续抛出
      }
    }
    dialogVisible.value = false
    fetchMovies()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 处理页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchMovies()
}

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 重置到第一页
  fetchMovies()
}

// 监听筛选条件变化时重置页码
watch(filters, () => {
  currentPage.value = 1  // 重置到第一页
  fetchMovies()
}, { deep: true })

// 监听排序方式变化时重置页码
watch(sortBy, () => {
  currentPage.value = 1  // 重置到第一页
  fetchMovies()
})

// 获取观看状态文本
const getWatchStatusText = (status) => {
  const statusMap = {
    'watched': '已看',
    'watching': '在看',
    'want_to_watch': '想看'
  }
  return statusMap[status] || ''
}

// 获取观看状态样式类
const getWatchStatusClass = (status) => {
  const classMap = {
    'watched': 'status-watched',
    'watching': 'status-watching',
    'want_to_watch': 'status-want'
  }
  return classMap[status] || ''
}

// 添加打开 TMDB 的方法
const openTMDB = (movie) => {
  const baseUrl = movie.type === 'movie' 
    ? 'https://www.themoviedb.org/movie/'
    : 'https://www.themoviedb.org/tv/'
  window.open(`${baseUrl}${movie.tmdb_id}`, '_blank')
}

// 计算已观看的电影列表
const watchedMovies = computed(() => {
  return movies.value
    .filter(movie => movie.watch_status === 'watched')
    .sort((a, b) => new Date(b.watch_date) - new Date(a.watch_date))
})

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

// 获取时间线项的类型
const getTimelineItemType = (movie) => {
  if (movie.rating >= 4) return 'success'
  if (movie.rating >= 3) return 'warning'
  return 'info'
}

// 选择类型
const selectType = (type) => {
  searchType.value = type
  nextStep()
}

// 上一步
const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 下一步
const nextStep = () => {
  if (activeStep.value < 3 && canGoNext.value) {
    activeStep.value++
    // 如果是第二步（搜索），自动执行搜索
    if (activeStep.value === 2 && searchQuery.value) {
      handleSearch()
    }
  }
}

// 修改步骤2的搜索按钮点击事件
const handleSearchClick = () => {
  handleSearch()
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 24px;
  color: #1a1a1a;
}

.filters-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.filters-header {
  margin-bottom: 16px;
}

.filters-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 18px;
}

.filters-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-top: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.filter-group h4 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #606266;
}

.filter-group .el-select {
  width: 100%;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  padding: 24px;
  width: 100%;
}

.movie-card {
  width: 100%;
  transition: all 0.3s ease;
  overflow: hidden;
  cursor: pointer;
  border-radius: 12px;
}

.movie-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.movie-poster-wrapper {
  position: relative;
  padding-top: 150%;
}

.movie-poster {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 观看状态图标 */
.watch-status-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 12px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  backdrop-filter: blur(8px);
  z-index: 2;
}

.status-watched {
  background-color: rgba(103, 194, 58, 0.9);
  color: white;
}

.status-watching {
  background-color: rgba(230, 162, 60, 0.9);
  color: white;
}

.status-want {
  background-color: rgba(144, 147, 153, 0.9);
  color: white;
}

.watch-status-icon .el-icon {
  font-size: 15px;
}

.status-text {
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 信息浮层 */
.movie-info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
  padding: 80px 20px 20px;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s;
}

.movie-card:hover .movie-info-overlay {
  opacity: 1;
}

.movie-info {
  position: relative;
  z-index: 1;
}

.movie-title {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.movie-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.movie-rating {
  min-height: 24px;
  display: flex;
  align-items: center;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(45deg, #f5f7fa, #e4e7ed);
  color: #909399;
  font-size: 32px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-result-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.search-result-item:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-poster {
  width: 120px;
  height: 100%;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.result-original-title {
  margin: 0 0 4px;
  font-size: 14px;
  color: #606266;
}

.result-date {
  margin: 0 0 8px;
  font-size: 13px;
  color: #909399;
}

.result-overview {
  font-size: 13px;
  color: #606266;
  margin: 0;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.select-btn {
  position: absolute;
  right: 12px;
  top: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.search-result-item:hover .select-btn {
  opacity: 1;
}

.selected-movie {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.selected-poster {
  width: 100px;
  height: 150px;
  border-radius: 4px;
  overflow: hidden;
}

.selected-info {
  flex: 1;
}

.selected-info h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.selected-info p {
  margin: 0 0 4px;
  color: #606266;
  font-size: 14px;
}

.tmdb-search {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.movie-detail {
  margin-bottom: 24px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.movie-detail-header {
  display: flex;
  gap: 24px;
}

.detail-poster {
  width: 200px;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.detail-info {
  flex: 1;
}

.detail-title {
  margin: 0 0 8px;
  font-size: 24px;
  color: #1a1a1a;
}

.detail-original-title {
  margin: 0 0 16px;
  font-size: 16px;
  color: #606266;
}

.detail-date {
  margin: 0 0 16px;
  color: #909399;
}

.detail-tags {
  margin-bottom: 16px;
}

.detail-overview {
  color: #606266;
  line-height: 1.6;
}

.watch-info {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.watch-info-title {
  margin: 0 0 20px;
  font-size: 18px;
  color: #1a1a1a;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 添加下拉菜单样式 */
:deep(.filter-select-dropdown) {
  min-width: 120px !important;
}

/* 添加评分选项的样式 */
:deep(.el-rate) {
  display: inline-flex;
  align-items: center;
}

:deep(.el-select-dropdown__item) {
  padding: 0 12px;
  height: 40px;
  line-height: 40px;
}

/* 修改头部样式 */
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 调整标签样式 */
:deep(.el-tag) {
  border: none;
  padding: 4px 8px;
  height: 24px;
  line-height: 16px;
  font-size: 13px;
}

/* 调整评分样式 */
:deep(.el-rate__icon) {
  font-size: 18px;
  margin-right: 4px;
}

/* 优化分页样式 */
.pagination-container {
  margin-top: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

:deep(.el-pagination) {
  justify-content: center;
  font-size: 14px;
}

:deep(.el-select .el-input) {
  width: 110px;
}

:deep(.el-pagination button) {
  background: transparent;
}

:deep(.el-pagination .el-pager li) {
  background: transparent;
  border: none;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: #409eff;
  color: #fff;
  font-weight: bold;
}

:deep(.el-pagination .el-pager li:not(.is-active):hover) {
  color: #409eff;
}

/* 添加按钮样式 */
.detail-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.detail-actions .el-button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.detail-actions .el-icon {
  font-size: 16px;
}

/* 添加时间线视图样式 */
.timeline-view {
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  margin-top: 24px;
}

.timeline-card {
  --el-card-padding: 16px;
}

.timeline-content {
  display: flex;
  gap: 20px;
}

.timeline-poster {
  width: 120px;
  height: 180px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.timeline-info {
  flex: 1;
}

.timeline-title {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.timeline-original-title {
  margin: 0 0 12px;
  font-size: 14px;
  color: #606266;
}

.timeline-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.timeline-rating {
  min-height: 24px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.timeline-overview {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 16px;
}

.timeline-actions {
  display: flex;
  gap: 16px;
}

/* 视图切换按钮样式 */
:deep(.el-radio-button__inner) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-timeline-item__node) {
  width: 16px;
  height: 16px;
}

:deep(.el-timeline-item__timestamp) {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

/* 根据评分设置时间线节点颜色 */
:deep(.el-timeline-item.success .el-timeline-item__node) {
  background-color: var(--el-color-success);
}

:deep(.el-timeline-item.warning .el-timeline-item__node) {
  background-color: var(--el-color-warning);
}

:deep(.el-timeline-item.info .el-timeline-item__node) {
  background-color: var(--el-color-info);
}

/* 添加步骤相关样式 */
.dialog-steps {
  margin-bottom: 24px;
}

.step-content {
  min-height: 300px;
  padding: 20px 0;
}

.step-type h3,
.step-search h3,
.step-results h3,
.step-watch-info h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #303133;
}

.type-options {
  display: flex;
  gap: 24px;
  justify-content: center;
  padding: 40px 0;
}

.type-option {
  width: 160px;
  height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.type-option:hover {
  transform: translateY(-4px);
}

.type-option.is-selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.type-option .el-icon {
  font-size: 48px;
  color: var(--el-color-primary);
}

.type-option span {
  font-size: 16px;
  color: #303133;
}

.step-search {
  max-width: 500px;
  margin: 0 auto;
}

/* 优化搜索结果选中状态 */
.search-result-item.is-selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

/* 添加搜索框样式 */
.header-search {
  width: 240px;
  margin-left: 16px;
}

.header-search :deep(.el-input__wrapper) {
  border-radius: 20px;
}

.header-search :deep(.el-input__inner) {
  height: 32px;
  line-height: 32px;
}

.header-search :deep(.el-input__prefix) {
  color: #909399;
}

/* 搜索加载状态样式 */
.search-loading {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.step-search .el-input {
  margin-bottom: 20px;
}

/* 禁用状态样式 */
:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: var(--el-disabled-bg-color);
}

/* 添加未评分样式 */
.no-rating {
  color: #909399;
  font-size: 14px;
  font-style: italic;
}
</style> 