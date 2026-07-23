<script setup>
import {computed, onUnmounted, reactive, ref, watch} from "vue";
import {get, post} from "@/net";
import {copyIp, cpuNameToImage, fitByUnit, osNameToIcon, percentageToStatus, rename} from "@/tools";
import {ElMessage, ElMessageBox} from "element-plus";
import RuntimeHistory from "@/component/RuntimeHistory.vue";
import {Connection, Delete} from "@element-plus/icons-vue";

const locations = [
  {name: 'cn', desc: '中国大陆'},
  {name: 'hk', desc: '香港'},
  {name: 'jp', desc: '日本'},
  {name: 'us', desc: '美国'},
  {name: 'sg', desc: '新加坡'},
  {name: 'kr', desc: '韩国'},
  {name: 'de', desc: '德国'}
]

const props = defineProps({
  id: Number,
  update: Function
})
const emits = defineEmits(['delete', 'terminal'])

const details = reactive({
  base: {},
  runtime: {
    list: []
  },
  editNode: false
})
const nodeEdit = reactive({
  name: '',
  location: ''
})
const enableNodeEdit = () => {
  details.editNode = true
  nodeEdit.name = details.base.node
  nodeEdit.location = details.base.location
}
const submitNodeEdit = () => {
  post('/api/monitor/node', {
    id: props.id,
    node: nodeEdit.name,
    location: nodeEdit.location
  }, () => {
    details.editNode = false
    updateDetails()
    ElMessage.success('节点信息已更新')
  })
}

function deleteClient() {
  ElMessageBox.confirm('删除此主机后所有统计数据都将丢失，您确定要这样做吗？', '删除主机', {
    confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
  }).then(() => {
    get(`/api/monitor/delete?clientId=${props.id}`, () => {
      emits('delete')
      props.update()
      ElMessage.success('主机已成功移除')
    })
  }).catch(() => {})
}

function updateDetails() {
  props.update()
  init(props.id)
}

const monitorRanges = [
  {label: '5分钟', value: 5},
  {label: '15分钟', value: 15},
  {label: '1小时', value: 60}
]
const monitorRange = ref(15)
const monitoring = ref(true)

const now = computed(() => details.runtime.list[details.runtime.list.length - 1])
const percentage = value => Math.min(100, Math.max(0, value || 0))
const cpuPercentage = computed(() => percentage(now.value?.cpuUsage * 100))
const memoryPercentage = computed(() => percentage(now.value?.memoryUsage / details.runtime.memory * 100))
const diskPercentage = computed(() => percentage(now.value?.diskUsage / details.runtime.disk * 100))
const lastUpdated = computed(() => {
  if(!now.value?.timestamp) return '等待数据'
  return new Date(now.value.timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})
})
const historyData = computed(() => {
  const list = details.runtime.list
  if(!list.length) return []
  const latest = new Date(list[list.length - 1].timestamp).getTime()
  const start = latest - monitorRange.value * 60 * 1000
  return list.filter(item => new Date(item.timestamp).getTime() >= start)
})

function refreshRuntime() {
  if(props.id === -1 || !details.runtime || !monitoring.value) return
  const clientId = props.id
  get(`/api/monitor/runtime-now?clientId=${clientId}`, data => {
    if(clientId !== props.id) return
    if(details.runtime.list.length >= 360)
      details.runtime.list.splice(0, 1)
    details.runtime.list.push(data)
  })
}

const refreshTimer = setInterval(refreshRuntime, 10000)
onUnmounted(() => clearInterval(refreshTimer))

const init = id => {
  if(id !== -1) {
    monitoring.value = true
    monitorRange.value = 15
    details.base = {}
    details.runtime = { list: [] }
    get(`/api/monitor/details?clientId=${id}`, data => {
      if(id === props.id) Object.assign(details.base, data)
    })
    get(`/api/monitor/runtime-history?clientId=${id}`, data => {
      if(id === props.id) Object.assign(details.runtime, data)
    })
  }
}
watch(() => props.id, init, { immediate: true })
</script>

<template>
  <el-scrollbar>
    <div class="client-details" v-loading="Object.keys(details.base).length === 0">
      <div v-if="Object.keys(details.base).length">
        <div class="details-header">
          <div class="title">
            <i class="fa-solid fa-server"></i>
            服务器信息
          </div>
          <div class="details-actions">
            <el-button :icon="Connection" type="info"
                       @click="emits('terminal', id)" plain text>SSH远程连接</el-button>
            <el-button :icon="Delete" type="danger" style="margin-left: 0"
                       @click="deleteClient" plain text>删除此主机</el-button>
          </div>
        </div>
        <el-divider style="margin: 10px 0"/>
        <div class="details-list">
          <div>
            <span>服务器ID</span>
            <span>{{details.base.id}}</span>
          </div>
          <div>
            <span>服务器名称</span>
            <span>{{details.base.name}}</span>&nbsp;
            <i @click.stop="rename(details.base.id, details.base.name, updateDetails)"
               class="fa-solid fa-pen-to-square interact-item"/>
          </div>
          <div>
            <span>运行状态</span>
            <span>
            <i style="color: #18cb18" class="fa-solid fa-circle-play" v-if="details.base.online"></i>
            <i style="color: #18cb18" class="fa-solid fa-circle-stop" v-else></i>
            {{details.base.online ? '运行中' : '离线'}}
          </span>
          </div>
          <div v-if="!details.editNode">
            <span>服务器节点</span>
            <span :class="`flag-icon flag-icon-${details.base.location}`"></span>&nbsp;
            <span>{{details.base.node}}</span>&nbsp;
            <i @click.stop="enableNodeEdit"
               class="fa-solid fa-pen-to-square interact-item"/>
          </div>
          <div v-else>
            <span>服务器节点</span>
            <div style="display: inline-block;height: 15px">
              <div style="display: flex">
                <el-select v-model="nodeEdit.location" style="width: 80px" size="small">
                  <el-option v-for="item in locations" :value="item.name">
                    <span :class="`flag-icon flag-icon-${item.name}`"></span>&nbsp;
                    {{item.desc}}
                  </el-option>
                </el-select>
                <el-input v-model="nodeEdit.name" style="margin-left: 10px"
                          size="small" placeholder="请输入节点名称..."/>
                <div style="margin-left: 10px">
                  <i @click.stop="submitNodeEdit" class="fa-solid fa-check interact-item"/>
                </div>
              </div>
            </div>
          </div>
          <div>
            <span>公网IP地址</span>
            <span>
            {{details.base.ip}}
            <i class="fa-solid fa-copy interact-item" style="color: dodgerblue" @click.stop="copyIp(details.base.ip)"></i>
          </span>
          </div>
          <div style="display: flex">
            <span>处理器</span>
            <span>{{details.base.cpuName}}</span>
            <el-image style="height: 20px;margin-left: 10px"
                      :src="`/cpu-icons/${cpuNameToImage(details.base.cpuName)}`"/>
          </div>
          <div>
            <span>硬件配置信息</span>
            <span>
            <i class="fa-solid fa-microchip"></i>
            <span style="margin-right: 10px">{{` ${details.base.cpuCore} CPU 核心数 /`}}</span>
            <i class="fa-solid fa-memory"></i>
            <span>{{` ${details.base.memory.toFixed(1)} GB 内存容量`}}</span>
          </span>
          </div>
          <div>
            <span>操作系统</span>
            <i :style="{color: osNameToIcon(details.base.osName).color}"
               :class="`fa-brands ${osNameToIcon(details.base.osName).icon}`"></i>
            <span style="margin-left: 10px">{{`${details.base.osName} ${details.base.osVersion}`}}</span>
          </div>
        </div>
        <div class="monitor-header">
          <div>
            <div class="title">
              <i class="fa-solid fa-gauge-high"></i>
              实时监控
            </div>
            <div class="monitor-status">
              <span :class="['status-dot', {paused: !monitoring}]"/>
              <span>{{monitoring ? '每10秒自动更新' : '实时刷新已暂停'}}</span>
              <span>· 最后更新 {{lastUpdated}}</span>
            </div>
          </div>
          <div class="monitor-actions">
            <el-radio-group v-model="monitorRange" size="small">
              <el-radio-button v-for="range in monitorRanges" :key="range.value" :label="range.value">
                {{range.label}}
              </el-radio-button>
            </el-radio-group>
            <el-button size="small" @click="monitoring = !monitoring">
              <i :class="monitoring ? 'fa-solid fa-pause' : 'fa-solid fa-play'"/>
              <span style="margin-left: 6px">{{monitoring ? '暂停' : '继续'}}</span>
            </el-button>
          </div>
        </div>
        <el-divider style="margin: 12px 0 16px"/>
        <div v-if="details.base.online" v-loading="!details.runtime.list.length"
             style="min-height: 200px">
          <div class="metric-grid" v-if="details.runtime.list.length">
            <div class="metric-item">
              <div class="metric-label"><i class="fa-solid fa-microchip"/> CPU 使用率</div>
              <div class="metric-value">{{cpuPercentage.toFixed(1)}}<span>%</span></div>
              <el-progress :status="percentageToStatus(cpuPercentage)" :percentage="cpuPercentage"
                           :stroke-width="5" :show-text="false"/>
            </div>
            <div class="metric-item">
              <div class="metric-label"><i class="fa-solid fa-memory"/> 内存使用率</div>
              <div class="metric-value">{{memoryPercentage.toFixed(1)}}<span>%</span></div>
              <div class="metric-desc">{{now.memoryUsage.toFixed(1)}} / {{details.runtime.memory.toFixed(1)}} GB</div>
            </div>
            <div class="metric-item">
              <div class="metric-label"><i class="fa-solid fa-arrow-right-arrow-left"/> 网络吞吐</div>
              <div class="metric-network">
                <span><i class="fa-solid fa-arrow-up"/> {{fitByUnit(now.networkUpload, 'KB')}}/s</span>
                <span><i class="fa-solid fa-arrow-down"/> {{fitByUnit(now.networkDownload, 'KB')}}/s</span>
              </div>
              <div class="metric-desc">上传 / 下载</div>
            </div>
            <div class="metric-item">
              <div class="metric-label"><i class="fa-solid fa-hard-drive"/> 磁盘容量</div>
              <div class="metric-value">{{diskPercentage.toFixed(1)}}<span>%</span></div>
              <div class="metric-desc">{{now.diskUsage.toFixed(1)}} / {{details.runtime.disk.toFixed(1)}} GB</div>
            </div>
          </div>
          <runtime-history class="runtime-history" :data="historyData" :memory="details.runtime.memory"/>
        </div>
        <el-empty description="服务器处于离线状态，请检查服务器是否正常运行" v-else/>
      </div>
    </div>
  </el-scrollbar>
</template>

<style scoped>
.interact-item {
  transition: .3s;

  &:hover {
    cursor: pointer;
    scale: 1.1;
    opacity: 0.8;
  }
}

.client-details {
  height: 100%;
  padding: 24px;
  box-sizing: border-box;

  .title {
    color: dodgerblue;
    font-size: 18px;
    font-weight: bold;
  }

  .details-list {
    font-size: 14px;

    & div {
      margin-bottom: 10px;

      & span:first-child {
        color: gray;
        font-size: 13px;
        font-weight: normal;
        width: 120px;
        display: inline-block;
      }

      & span {
        font-weight: bold;
      }
    }
  }
}

.monitor-header {
  margin-top: 24px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.details-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.details-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.monitor-status {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--el-color-success);

  &.paused {
    background-color: var(--el-text-color-placeholder);
  }
}

.monitor-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-item {
  min-width: 0;
  padding: 14px;
  border: solid 1px var(--el-border-color-lighter);
  border-radius: 6px;
  background-color: var(--el-fill-color-lighter);
}

.metric-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.metric-value {
  margin: 6px 0;
  color: var(--el-text-color-primary);
  font-size: 24px;
  font-weight: bold;

  & span {
    margin-left: 3px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
    font-weight: normal;
  }
}

.metric-network {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin: 7px 0;
  color: var(--el-text-color-primary);
  font-size: 13px;

  & span:first-child i {
    color: var(--el-color-warning);
  }

  & span:last-child i {
    color: var(--el-color-primary);
  }
}

.metric-desc {
  overflow: hidden;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.runtime-history {
  margin-top: 26px;
}

@media (max-width: 900px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .client-details {
    padding: 16px;
  }

  .monitor-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .details-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }

  .details-actions {
    justify-content: flex-start;
  }

  .monitor-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
