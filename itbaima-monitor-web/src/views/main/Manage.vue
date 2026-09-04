<script setup>
import PreviewCard from "@/component/PreviewCard.vue";
import {computed, reactive, ref, watch} from "vue";
import {get} from "@/net";
import ClientDetails from "@/component/ClientDetails.vue";
import RegisterCard from "@/component/RegisterCard.vue";
import {Filter, Plus} from "@element-plus/icons-vue";
import {useRoute} from "vue-router";
import {useStore} from "@/store";
import TerminalWindow from "@/component/TerminalWindow.vue";
import {useWindowSize} from "@vueuse/core";

const locations = [
  {name: 'cn', desc: '中国大陆'},
  {name: 'hk', desc: '香港'},
  {name: 'jp', desc: '日本'},
  {name: 'us', desc: '美国'},
  {name: 'sg', desc: '新加坡'},
  {name: 'kr', desc: '韩国'},
  {name: 'de', desc: '德国'}
]
const checkedNodes = ref([])
const checkedSystems = ref([])
const searchKeyword = ref('')
const statusFilter = ref('all')
const cpuCategory = ref('all')
const memorySort = ref('default')

const activeFilterCount = computed(() => {
  return (searchKeyword.value.trim() ? 1 : 0) +
    (statusFilter.value !== 'all' ? 1 : 0) +
    (cpuCategory.value !== 'all' ? 1 : 0) +
    (memorySort.value !== 'default' ? 1 : 0) +
    (checkedSystems.value.length ? 1 : 0) +
    (checkedNodes.value.length ? 1 : 0)
})
const clearFilters = () => {
  searchKeyword.value = ''
  statusFilter.value = 'all'
  cpuCategory.value = 'all'
  memorySort.value = 'default'
  checkedSystems.value = []
  checkedNodes.value = []
}

const list = ref([])
const store = useStore()

const route = useRoute()
const { width } = useWindowSize()
const detailDrawerSize = computed(() => {
  if(width.value < 700) return 'calc(100% - 12px)'
  if(width.value < 1100) return '78%'
  return '860px'
})

const updateList = () => {
  if(route.name === 'manage') {
    get('/api/monitor/list', data => list.value = data)
  }
}
setInterval(updateList, 10000)
updateList()

const detail = reactive({
  show: false,
  id: -1
})
const displayClientDetails = (id) => {
  detail.show = true
  detail.id = id
}

const systems = computed(() => [...new Set(list.value.map(item => item.osName).filter(Boolean))].sort())

const clientList = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  const filtered = list.value.filter(item => {
    const matchesLocation = checkedNodes.value.length === 0 || checkedNodes.value.includes(item.location)
    const matchesSystem = checkedSystems.value.length === 0 || checkedSystems.value.includes(item.osName)
    const matchesStatus = statusFilter.value === 'all' ||
      (statusFilter.value === 'online' ? item.online : !item.online)
    const cpu = Number(item.cpuUsage) || 0
    const matchesCpu = cpuCategory.value === 'all' ||
      (cpuCategory.value === 'low' && cpu < 0.3) ||
      (cpuCategory.value === 'medium' && cpu >= 0.3 && cpu < 0.7) ||
      (cpuCategory.value === 'high' && cpu >= 0.7)
    const matchesKeyword = !keyword || [item.ip, item.name, item.id]
      .some(value => String(value ?? '').toLowerCase().includes(keyword))
    return matchesLocation && matchesSystem && matchesStatus && matchesCpu && matchesKeyword
  })
  const sorted = [...filtered]
  if(memorySort.value === 'asc') {
    sorted.sort((a, b) => (Number(a.memory) || 0) - (Number(b.memory) || 0))
  } else if(memorySort.value === 'desc') {
    sorted.sort((a, b) => (Number(b.memory) || 0) - (Number(a.memory) || 0))
  }
  return sorted
})

const currentPage = ref(1)
const pageSize = ref(24)
const pagedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return clientList.value.slice(start, start + pageSize.value)
})
watch(() => [clientList.value.length, pageSize.value], () => {
  const maxPage = Math.max(1, Math.ceil(clientList.value.length / pageSize.value))
  if(currentPage.value > maxPage) currentPage.value = maxPage
})
watch(() => [searchKeyword.value, statusFilter.value, cpuCategory.value, memorySort.value,
  checkedSystems.value.join(','), checkedNodes.value.join(',')], () => {
  currentPage.value = 1
})

const stats = computed(() => {
  const online = clientList.value.filter(item => item.online).length
  return {
    total: clientList.value.length,
    online,
    offline: clientList.value.length - online
  }
})

const register = reactive({
  show: false,
  token: ''
})
const refreshToken = () => get('/api/monitor/register', token => register.token = token)

function openTerminal(id) {
  terminal.show = true
  terminal.id = id
  detail.show = false
}
const terminal = reactive({
  show: false,
  id: -1
})
</script>

<template>
  <div class="manage-main">
    <div style="display: flex;justify-content: space-between;align-items: end">
      <div>
        <div class="title"><i class="fa-solid fa-server"></i> 管理主机列表</div>
        <div class="desc">在这里管理所有已经注册的主机实例，实时监控主机运行状态，快速进行管理和操作。</div>
      </div>
      <div>
        <el-button :icon="Plus" type="primary" plain :disabled="!store.isAdmin"
                   @click="register.show = true">添加新主机</el-button>
      </div>
    </div>
    <el-divider style="margin: 10px 0"/>
    <div class="stats-bar">
      <span>共 <b>{{ stats.total }}</b> 台主机</span>
      <el-divider direction="vertical"/>
      <span><i style="color: #18cb18" class="fa-solid fa-circle-play"></i> 在线 <b>{{ stats.online }}</b> 台</span>
      <el-divider direction="vertical"/>
      <span><i style="color: #8a8a8a" class="fa-solid fa-circle-stop"></i> 离线 <b>{{ stats.offline }}</b> 台</span>
    </div>
    <div class="toolbar">
      <el-popover placement="bottom-start" :width="360" trigger="click">
        <template #reference>
          <el-button :icon="Filter" plain>
            筛选器
            <el-badge v-if="activeFilterCount" :value="activeFilterCount" class="filter-badge"/>
          </el-button>
        </template>
        <div class="filter-panel">
          <div class="filter-title">
            <span>主机筛选</span>
            <el-button link type="primary" @click="clearFilters">清空条件</el-button>
          </div>
          <el-input v-model="searchKeyword" clearable placeholder="按 IP、主机名或 ID 检索"/>
          <div class="filter-label">系统分类</div>
          <el-checkbox-group v-model="checkedSystems" class="filter-systems">
            <el-checkbox v-for="system in systems" :key="system" :label="system">
              {{ system }}
            </el-checkbox>
          </el-checkbox-group>
          <div class="filter-label">在线状态</div>
          <el-radio-group v-model="statusFilter" class="filter-status">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="online">在线</el-radio-button>
            <el-radio-button label="offline">离线</el-radio-button>
          </el-radio-group>
          <div class="filter-label">CPU 使用率分类</div>
          <el-select v-model="cpuCategory" placeholder="CPU 分类" class="filter-sort">
            <el-option label="全部" value="all"/>
            <el-option label="低负载（< 30%）" value="low"/>
            <el-option label="中负载（30% - 70%）" value="medium"/>
            <el-option label="高负载（≥ 70%）" value="high"/>
          </el-select>
          <div class="filter-label">内存容量排序</div>
          <el-select v-model="memorySort" placeholder="内存排序" class="filter-sort">
            <el-option label="默认顺序" value="default"/>
            <el-option label="内存大小升序" value="asc"/>
            <el-option label="内存大小降序" value="desc"/>
          </el-select>
          <div class="filter-label">地区</div>
          <el-checkbox-group v-model="checkedNodes" class="filter-locations">
            <el-checkbox v-for="node in locations" :key="node.name" :label="node.name">
              <span :class="`flag-icon flag-icon-${node.name}`"></span>
              <span style="font-size: 13px;margin-left: 6px">{{node.desc}}</span>
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </el-popover>
    </div>
    <div class="card-list" v-if="pagedList.length">
      <transition-group name="card-pop" appear>
        <preview-card v-for="item in pagedList" :key="item.id" :data="item" :update="updateList"
                      @click="displayClientDetails(item.id)"/>
      </transition-group>
    </div>
    <div class="pager-bar" v-if="clientList.length > pageSize">
      <el-pagination background layout="prev, pager, next, sizes, total"
                     :total="clientList.length"
                     :page-sizes="[24, 48, 96, 200]"
                     v-model:current-page="currentPage"
                     v-model:page-size="pageSize"/>
    </div>
    <el-empty :description="list.length ? '没有匹配的主机' : '还没有任何主机哦，点击右上角添加一个吧'" v-else/>
    <el-drawer :size="detailDrawerSize" :show-close="false" v-model="detail.show"
               :with-header="false" v-if="list.length" @close="detail.id = -1">
      <client-details :id="detail.id" :update="updateList" @delete="updateList" @terminal="openTerminal"/>
    </el-drawer>
    <el-drawer v-model="register.show" direction="btt" :with-header="false"
               style="width: 600px;margin: 10px auto" size="320" @open="refreshToken">
      <register-card :token="register.token"/>
    </el-drawer>
    <el-drawer style="width: 800px" :size="520" direction="btt"
               @close="terminal.id = -1"
               v-model="terminal.show" :close-on-click-modal="false">
      <template #header>
        <div>
          <div style="font-size: 18px;color: dodgerblue;font-weight: bold;">SSH远程连接</div>
          <div style="font-size: 14px">
            远程连接的建立将由服务端完成，因此在内网环境下也可以正常使用。
          </div>
        </div>
      </template>
      <terminal-window :id="terminal.id"/>
    </el-drawer>
  </div>
</template>

<style scoped>
:deep(.el-drawer__header) {
  margin-bottom: 10px;
}

:deep(.el-checkbox-group .el-checkbox) {
  margin-right: 10px;
}

:deep(.el-drawer) {
  margin: 10px;
  height: calc(100% - 20px);
  border-radius: 10px;
}

:deep(.el-drawer__body) {
  padding: 0;
}

@media (max-width: 700px) {
  :deep(.el-drawer) {
    margin: 6px;
    height: calc(100% - 12px);
  }
}

.manage-main {
  margin: 0 50px;

  .title {
    font-size: 22px;
    font-weight: bold;
  }

  .desc {
    font-size: 15px;
    color: grey;
  }

  .stats-bar {
    font-size: 14px;
    color: grey;
    margin-bottom: 15px;

    b {
      color: var(--el-text-color-primary);
    }
  }

  .toolbar {
    display: flex;
    gap: 12px;
    margin-bottom: 15px;
  }

}

.card-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

@media (max-width: 700px) {
  .manage-main {
    margin: 0 15px;
  }

  .toolbar {
    flex-direction: column;
  }

  .filter-panel {
    width: 100%;
  }
}

.filter-badge {
  margin-left: 8px;
}

.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.filter-sort {
  width: 100%;
}

.filter-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.filter-systems,
.filter-locations {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.filter-status {
  width: 100%;
}

.filter-status :deep(.el-radio-button) {
  flex: 1;
}

.filter-status :deep(.el-radio-button__inner) {
  width: 100%;
}

.filter-locations {
}

.card-pop-enter-active {
  transition: opacity .4s ease, transform .4s cubic-bezier(.22, .61, .36, 1);
}

.card-pop-enter-active:nth-child(2) { transition-delay: .06s; }
.card-pop-enter-active:nth-child(3) { transition-delay: .12s; }
.card-pop-enter-active:nth-child(4) { transition-delay: .18s; }
.card-pop-enter-active:nth-child(n+5) { transition-delay: .24s; }

.card-pop-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(.96);
}

.card-pop-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}

.card-pop-leave-to {
  opacity: 0;
  transform: scale(.95);
}

.card-pop-move {
  transition: transform .35s cubic-bezier(.22, .61, .36, 1);
}
</style>
