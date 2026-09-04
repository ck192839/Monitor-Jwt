<script setup>
import {computed} from 'vue'
import {copyIp, fitByUnit, osNameToIcon, percentageToStatus, rename} from '@/tools'

const props = defineProps({
  data: Object,
  update: Function
})

const clampPercent = value => Math.min(100, Math.max(0, Number(value) || 0))
const cpuPercent = computed(() => clampPercent((props.data?.cpuUsage ?? 0) * 100))
const memoryPercent = computed(() => {
  const memory = Number(props.data?.memory) || 0
  return memory > 0 ? clampPercent((Number(props.data?.memoryUsage) || 0) / memory * 100) : 0
})
</script>

<template>
  <div class="instance-card">
    <div style="display: flex;justify-content: space-between">
      <div>
        <div class="name">
          <span :class="`flag-icon flag-icon-${data.location}`"></span>
          <span style="margin: 0 5px">{{ data.name }}</span>
          <i class="fa-solid fa-pen-to-square interact-item" @click.stop="rename(data.id, data.name, update)"></i>
        </div>
        <div class="os">
          操作系统:
          <i :style="{color: osNameToIcon(data.osName).color}"
             :class="`fa-brands ${osNameToIcon(data.osName).icon}`"></i>
          {{`${data.osName || '未知'} ${data.osVersion || ''}`}}
        </div>
      </div>
      <div class="status" v-if="data.online">
        <i style="color: #18cb18" class="fa-solid fa-circle-play"></i>
        <span style="margin-left: 5px">运行中</span>
      </div>
      <div class="status" v-else>
        <i style="color: #8a8a8a" class="fa-solid fa-circle-stop"></i>
        <span style="margin-left: 5px">离线</span>
      </div>
    </div>
    <el-divider style="margin: 10px 0"/>
    <div class="network">
      <span style="margin-right: 10px">公网IP: {{data.ip}}</span>
      <i class="fa-solid fa-copy interact-item" @click.stop="copyIp(data.ip)" style="color: dodgerblue"></i>
    </div>
    <div class="cpu">
      <span style="margin-right: 10px">处理器: {{data.cpuName || '未知'}}</span>
    </div>
    <div class="hardware">
      <i class="fa-solid fa-microchip"></i>
      <span style="margin-right: 10px">{{` ${data.cpuCore} CPU`}}</span>
      <i class="fa-solid fa-memory"></i>
      <span>{{` ${Number(data.memory || 0).toFixed(1)} GB`}}</span>
    </div>
    <div class="progress">
      <span>{{`CPU: ${cpuPercent.toFixed(1)}%`}}</span>
      <el-progress :status="percentageToStatus(cpuPercent)"
                   :percentage="cpuPercent" :stroke-width="5" :show-text="false"/>
    </div>
    <div class="progress">
      <span>内存: <b>{{Number(data.memoryUsage || 0).toFixed(1)}}</b> GB</span>
      <el-progress :status="percentageToStatus(memoryPercent)"
                   :percentage="memoryPercent" :stroke-width="5" :show-text="false"/>
    </div>
    <div class="network-flow">
      <div>网络流量</div>
      <div>
        <i class="fa-solid fa-arrow-up"></i>
        <span>{{` ${fitByUnit(data.networkUpload, 'KB')}/s`}}</span>
        <el-divider direction="vertical"/>
        <i class="fa-solid fa-arrow-down"></i>
        <span>{{` ${fitByUnit(data.networkDownload, 'KB')}/s`}}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dark .instance-card { color: #d9d9d9 }

.interact-item {
  transition: .3s;

  &:hover {
    cursor: pointer;
    scale: 1.1;
    opacity: 0.8;
  }
}

.instance-card {
  width: 320px;
  padding: 15px;
  background-color: var(--el-bg-color);
  border-radius: 5px;
  box-sizing: border-box;
  color: #606060;
  transition: .3s;

  &:hover {
    cursor: pointer;
    scale: 1.02;
  }

  .name {
    font-size: 15px;
    font-weight: bold;
  }

  .status {
    font-size: 14px;
  }

  .os {
    font-size: 13px;
    color: grey;
  }

  .network {
    font-size: 13px;
  }

  .hardware {
    margin-top: 5px;
    font-size: 13px;
  }

  .progress {
    margin-top: 10px;
    font-size: 12px;
  }

  .cpu {
    font-size: 13px;
  }

  .network-flow {
    margin-top: 10px;
    font-size: 12px;
    display: flex;
    justify-content: space-between;
  }
}
</style>
