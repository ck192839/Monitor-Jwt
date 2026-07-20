import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  optimizeDeps: {
    include: [
      'element-plus/es',
      'element-plus/es/components/base/style/css',
      'element-plus/es/components/container/style/css',
      'element-plus/es/components/main/style/css',
      'element-plus/es/components/header/style/css',
      'element-plus/es/components/dropdown/style/css',
      'element-plus/es/components/dropdown-menu/style/css',
      'element-plus/es/components/dropdown-item/style/css',
      'element-plus/es/components/icon/style/css',
      'element-plus/es/components/avatar/style/css',
      'element-plus/es/components/tag/style/css',
      'element-plus/es/components/switch/style/css',
      'element-plus/es/components/image/style/css',
      'element-plus/es/components/drawer/style/css',
      'element-plus/es/components/empty/style/css',
      'element-plus/es/components/checkbox-group/style/css',
      'element-plus/es/components/checkbox/style/css',
      'element-plus/es/components/divider/style/css',
      'element-plus/es/components/button/style/css',
      'element-plus/es/components/progress/style/css',
      'element-plus/es/components/loading/style/css',
      'element-plus/es/components/scrollbar/style/css',
      'element-plus/es/components/select/style/css',
      'element-plus/es/components/option/style/css',
      'element-plus/es/components/form/style/css',
      'element-plus/es/components/form-item/style/css',
      'element-plus/es/components/input/style/css',
      'element-plus/es/components/row/style/css',
      'element-plus/es/components/link/style/css',
      'element-plus/es/components/col/style/css',
      'element-plus/es/components/steps/style/css',
      'element-plus/es/components/step/style/css'
    ]
  }
})
