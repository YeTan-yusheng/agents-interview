import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // dev 代理：浏览器请求 5173/api/... 时，vite 开发服务器把它转发给 8000 的后端
      "/api": "http://127.0.0.1:8000",
    },
  },
})
