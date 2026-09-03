<script setup>
defineProps({
  name: String,
  active: Boolean
})
</script>

<template>
  <div :class="`tab-item ${active ? 'active' : ''}`">
    <span>{{name}}</span>
  </div>
</template>

<style scoped>
.tab-item {
  position: relative;
  font-size: 15px;
  width: 55px;
  height: 55px;
  text-align: center;
  line-height: 55px;
  box-sizing: border-box;
  transition: color .3s, transform .2s ease;

  &:hover {
    cursor: pointer;
    color: var(--el-color-primary);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0) scale(.95);
  }

  &::after {
    content: '';
    position: absolute;
    left: 50%;
    bottom: 0;
    width: 0;
    height: 2px;
    border-radius: 1px;
    background-color: var(--el-color-primary);
    transform: translateX(-50%);
    transition: width .3s cubic-bezier(.22, .61, .36, 1);
  }
}

.tab-item.active {
  color: var(--el-color-primary);
}

.active::after {
  width: 100%;
}
</style>
