<template>
  <footer class="site-footer">
    <div class="container">
      <div class="footer-content">
        <div class="about-site">
          <h3>关于本站</h3>
          <p>XiaoZhangBlog 是一个分享技术、生活和影视作品的个人博客。</p>
          <p>希望能为您带来有价值的内容和愉快的阅读体验。</p>
        </div>
        <div class="contact-info">
          <h3>联系方式</h3>
          <p>Email: xiaozhangs@example.com</p>
          <p>微信公众号: XiaoZhangBlog</p>
        </div>
      </div>
      <div class="copyright">
        © {{ currentYear }} XiaoZhangBlog. All Rights Reserved.
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

// 获取当前年份
const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.site-footer {
  background-color: #2c3e50;
  color: white;
  padding: 50px 0 20px;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.about-site h3, .contact-info h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
}

.about-site p, .contact-info p {
  margin: 5px 0;
  opacity: 0.8;
}

.copyright {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 14px;
  opacity: 0.7;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style> 