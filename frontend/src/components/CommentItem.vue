<template>
  <div class="comment-item">
    <div class="comment-header">
      <div class="user-info">
        <el-avatar 
          :size="32" 
          :src="getImageUrl(comment.user?.avatar)"
          :icon="UserFilled"
        />
        <div class="user-meta">
          <span class="username">{{ comment.user?.username }}</span>
          <span class="time">{{ new Date(comment.created_at).toLocaleString() }}</span>
        </div>
      </div>
      <div class="comment-actions">
        <el-button 
          link 
          type="primary" 
          @click="handleReply"
        >
          <el-icon><ChatLineRound /></el-icon>
          回复
        </el-button>
        <el-button 
          v-if="comment.user_id === currentUser?.id"
          link 
          type="danger" 
          @click="handleDelete"
        >
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </div>
    <div class="comment-content">{{ comment.content }}</div>
    
    <!-- 回复输入框 -->
    <div v-if="isReplying" class="reply-input">
      <el-input
        v-model="replyContent"
        type="textarea"
        :rows="2"
        placeholder="写下你的回复..."
        :maxlength="300"
        show-word-limit
      />
      <div class="reply-actions">
        <el-button @click="cancelReply">取消</el-button>
        <el-button 
          type="primary"
          @click="submitReply"
        >
          发表回复
        </el-button>
      </div>
    </div>

    <!-- 递归渲染子评论 -->
    <div v-if="comment.replies?.length > 0" class="replies-section">
      <comment-item
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :current-user="currentUser"
        :article-id="articleId"
        @refresh="$emit('refresh')"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, ChatLineRound, Delete } from '@element-plus/icons-vue'
import axios from '../utils/axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  currentUser: {
    type: Object,
    default: null
  },
  articleId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['refresh'])

const isReplying = ref(false)
const replyContent = ref('')

const getImageUrl = (path) => {
  if (!path) return ''
  return `${axios.defaults.baseURL}${path}`
}

const handleReply = () => {
  isReplying.value = true
}

const cancelReply = () => {
  isReplying.value = false
  replyContent.value = ''
}

const submitReply = async () => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  if (!props.currentUser) {
    ElMessage.warning('请先登录后再评论')
    localStorage.setItem('redirectPath', window.location.pathname)
    router.push('/login')
    return
  }

  try {
    await axios.post('/v1/comments/', {
      content: replyContent.value,
      article_id: props.articleId,
      parent_id: props.comment.id
    })
    
    replyContent.value = ''
    isReplying.value = false
    emit('refresh')
    ElMessage.success('回复成功')
  } catch (error) {
    ElMessage.error('回复失败')
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条评论吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/v1/comments/${props.comment.id}`)
    ElMessage.success('删除成功')
    emit('refresh')
  } catch (error) {
    if (error === 'cancel') return
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.comment-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  font-size: 14px;
  line-height: 1.6;
  padding: 8px 0 8px 44px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.reply-input {
  margin: 12px 0 12px 44px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.replies-section {
  margin-left: 44px;
  margin-top: 12px;
  padding-left: 20px;
  border-left: 2px solid #ebeef5;
}
</style> 