<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 更新页面标题函数
const updateTitle = () => {
  let title = '小张博客'
  
  // 根据路由路径设置不同的标题
  if (route.path === '/') {
    title = '首页 - 小张博客'
  } else if (route.path === '/movies') {
    title = '影视分享 - 小张博客'
  } else if (route.path.startsWith('/article/')) {
    // 如果有文章标题，可以在路由元信息中获取
    const articleTitle = route.meta.title
    title = articleTitle ? `${articleTitle} - 小张博客` : '文章详情 - 小张博客'
  } else if (route.path === '/admin') {
    title = '管理后台 - 小张博客'
  }
  
  // 设置文档标题
  document.title = title
}

// 根据路由更新页面标题
watch(
  () => route.path,
  () => {
    updateTitle()
  },
  { immediate: true }
)
</script>

<style>
/* 重置全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  background-color: #f5f7fa;
}

#app {
  height: 100vh;
}

a {
  text-decoration: none;
  color: #409eff;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
