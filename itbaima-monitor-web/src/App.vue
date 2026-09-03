<script setup>
import { onMounted } from 'vue'
import { useDark } from '@vueuse/core'

useDark({
  selector: 'html',
  attribute: 'class',
  valueDark: 'dark',
  valueLight: 'light'
})

// 监听 html 的 class 变化，切换瞬间临时开启全局颜色过渡，结束后移除，
// 平时不影响按钮 hover 等自带的 transition
onMounted(() => {
  const el = document.documentElement
  let isDark = el.classList.contains('dark')
  new MutationObserver(() => {
    const nowDark = el.classList.contains('dark')
    if (nowDark === isDark) return
    isDark = nowDark
    if (performance.now() < 600) return // 首次挂载恢复上次主题时不做动画
    el.classList.add('theme-switching')
    clearTimeout(el._themeSwitchTimer)
    el._themeSwitchTimer = setTimeout(() => el.classList.remove('theme-switching'), 400)
  }).observe(el, { attributes: true, attributeFilter: ['class'] })
})

</script>

<template>
  <header>
    <div class="wrapper">
      <router-view/>
    </div>
  </header>
</template>

<style>
/* 夜间模式切换瞬间的全局颜色过渡（由 .theme-switching 临时启用） */
.theme-switching,
.theme-switching *,
.theme-switching *::before,
.theme-switching *::after {
  transition: background-color .3s ease, color .3s ease,
    border-color .3s ease, fill .3s ease, stroke .3s ease,
    box-shadow .3s ease !important;
}

html {
  background-color: var(--el-bg-color);
}
</style>

<style scoped>
header {
  line-height: 1.5;
}
</style>
