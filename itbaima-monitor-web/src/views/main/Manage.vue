<script setup>
import PreviewCard from "@/component/PreviewCard.vue";
import {computed, reactive, ref, watch} from "vue";
import {get} from "@/net";
import ClientDetails from "@/component/ClientDetails.vue";
import RegisterCard from "@/component/RegisterCard.vue";
import {Plus} from "@element-plus/icons-vue";
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

const clientList = computed(() => {
  if(checkedNodes.value.length === 0) {
    return list.value
  } else {
    return list.value.filter(item => checkedNodes.value.indexOf(item.location) >= 0)
  }
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
    <div style="margin-bottom: 20px">
      <el-checkbox-group v-model="checkedNodes">
        <el-checkbox v-for="node in locations" :key="node" :label="node.name" border>
          <span :class="`flag-icon flag-icon-${node.name}`"></span>
          <span style="font-size: 13px;margin-left: 10px">{{node.desc}}</span>
        </el-checkbox>
      </el-checkbox-group>
    </div>
    <div class="card-list" v-if="list.length">
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
    <el-empty description="还没有任何主机哦，点击右上角添加一个吧" v-else/>
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
}

.card-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
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
