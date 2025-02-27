import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)
app.mount('#app')

// // 屏蔽 ResizeObserver 良性错误
// const debounce = (fn, delay = 100) => {
//     let timer = null;
//     return (...args) => {
//       clearTimeout(timer);
//       timer = setTimeout(() => fn(...args), delay);
//     };
//   };
  
//   window.addEventListener('error', debounce(e => {
//     if (e.message.includes('ResizeObserver')) {
//       e.stopImmediatePropagation();
//       e.preventDefault();
//     }
//   }));
  
// 禁用 ResizeObserver 警告
const originalError = console.error
console.error = (...args) => {
  if (/ResizeObserver/.test(args[0])) return
  originalError.call(console, ...args)
}
  