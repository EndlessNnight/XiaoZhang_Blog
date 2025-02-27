export const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  // 移除开头的斜杠，避免双斜杠问题
  return `${axios.defaults.baseURL}${path.startsWith('/') ? path : '/' + path}`
} 