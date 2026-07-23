<template>
  <div class="welcome-page">
    <header class="welcome-header">
      <div class="brand">
        <el-image class="brand-logo"
                  src="https://element-plus.org/images/element-plus-logo.svg"/>
        <div class="brand-name">
          <strong>服务器监控平台</strong>
          <span>ITBAIMA MONITOR</span>
        </div>
      </div>
      <div class="header-actions">
        <div class="secure-state">
          <span class="status-dot"></span>
          安全访问
        </div>
        <el-switch v-model="dark" active-color="#424242"
                   :active-action-icon="Moon"
                   :inactive-action-icon="Sunny"/>
      </div>
    </header>
    <main class="welcome-main">
      <section class="platform-overview">
        <div class="overview-content">
          <div class="overview-title">
            <div class="section-label">
              <span class="status-dot"></span>
              监控控制台
            </div>
            <h1>服务器运行中心</h1>
            <p>CONTROL CENTER / 服务器监控</p>
          </div>
          <div class="monitor-panel" aria-label="服务器控制台预览">
            <div class="panel-header">
              <div>
                <strong>基础设施概览</strong>
                <span>CONTROL CENTER</span>
              </div>
              <el-tag type="success" size="small" effect="plain">等待登录</el-tag>
            </div>
            <div class="node-list">
              <div class="node-row">
                <div class="node-icon"><el-icon><Monitor/></el-icon></div>
                <div class="node-info">
                  <strong>计算节点</strong>
                  <span>CPU · 内存 · 运行状态</span>
                </div>
                <div class="signal-bars" aria-hidden="true">
                  <span></span><span></span><span></span><span></span><span></span>
                </div>
              </div>
              <div class="node-row">
                <div class="node-icon data"><el-icon><DataLine/></el-icon></div>
                <div class="node-info">
                  <strong>性能数据</strong>
                  <span>历史趋势 · 网络流量</span>
                </div>
                <div class="signal-bars warning" aria-hidden="true">
                  <span></span><span></span><span></span><span></span><span></span>
                </div>
              </div>
              <div class="node-row">
                <div class="node-icon terminal"><el-icon><Connection/></el-icon></div>
                <div class="node-info">
                  <strong>远程终端</strong>
                  <span>SSH · 实时会话</span>
                </div>
                <div class="node-status"><span class="status-dot"></span>就绪</div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="auth-column">
        <router-view v-slot="{ Component }">
          <transition name="el-fade-in-linear" mode="out-in">
            <component :is="Component"/>
          </transition>
        </router-view>
      </section>
    </main>
  </div>
</template>

<script setup>
import {ref} from "vue";
import {useDark} from "@vueuse/core";
import {Connection, DataLine, Monitor, Moon, Sunny} from "@element-plus/icons-vue";

const dark = ref(useDark())
</script>

<style scoped>
.welcome-page {
  width: 100vw;
  height: 100vh;
  min-height: 640px;
  overflow: hidden;
  color: var(--el-text-color-primary);
  background-color: var(--el-bg-color-page);
}

.welcome-page,
.welcome-page * {
  box-sizing: border-box;
}

.welcome-header {
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--el-bg-color);
  border-bottom: solid 1px var(--el-border-color);
}

.brand,
.header-actions,
.secure-state,
.section-label,
.panel-header,
.node-row {
  display: flex;
  align-items: center;
}

.brand-logo {
  width: 132px;
  height: 30px;
}

.brand-name {
  height: 34px;
  margin-left: 16px;
  padding-left: 16px;
  border-left: solid 1px var(--el-border-color);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand-name strong {
  font-size: 14px;
  line-height: 18px;
}

.brand-name span {
  color: var(--el-text-color-secondary);
  font-size: 10px;
  line-height: 14px;
}

.header-actions {
  gap: 20px;
}

.secure-state {
  gap: 7px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.status-dot {
  width: 7px;
  height: 7px;
  flex: none;
  border-radius: 50%;
  background-color: #18cb18;
  box-shadow: 0 0 0 3px #18cb1822;
}

.welcome-main {
  height: calc(100% - 64px);
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(390px, 440px);
}

.platform-overview {
  min-width: 0;
  padding: 56px;
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
}

.overview-content {
  width: min(100%, 760px);
  margin: 0 auto;
}

.section-label {
  gap: 9px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.overview-title h1 {
  margin: 14px 0 8px;
  font-size: 36px;
  line-height: 1.25;
}

.overview-title p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 15px;
}

.monitor-panel {
  margin-top: 38px;
  overflow: hidden;
  background-color: var(--el-bg-color);
  border: solid 1px var(--el-border-color);
  border-radius: 6px;
  box-shadow: var(--el-box-shadow-light);
}

.panel-header {
  min-height: 64px;
  padding: 0 20px;
  justify-content: space-between;
  border-bottom: solid 1px var(--el-border-color-lighter);
}

.panel-header > div {
  display: flex;
  flex-direction: column;
}

.panel-header strong {
  font-size: 15px;
}

.panel-header > div span {
  color: var(--el-text-color-secondary);
  font-size: 10px;
}

.node-list {
  padding: 4px 20px;
}

.node-row {
  min-height: 72px;
  border-bottom: solid 1px var(--el-border-color-lighter);
}

.node-row:last-child {
  border-bottom: none;
}

.node-icon {
  width: 36px;
  height: 36px;
  flex: none;
  border-radius: 5px;
  display: grid;
  place-items: center;
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.node-icon.data {
  color: #d18b19;
  background-color: #ffa04622;
}

.node-icon.terminal {
  color: #18a818;
  background-color: #18cb1822;
}

.node-info {
  min-width: 0;
  margin-left: 12px;
  display: flex;
  flex: 1;
  flex-direction: column;
}

.node-info strong {
  font-size: 14px;
}

.node-info span {
  margin-top: 3px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.signal-bars {
  width: 108px;
  height: 24px;
  display: flex;
  align-items: end;
  justify-content: flex-end;
  gap: 5px;
}

.signal-bars span {
  width: 9px;
  border-radius: 2px 2px 0 0;
  background-color: var(--el-color-primary-light-5);
}

.signal-bars span:nth-child(1) { height: 8px; }
.signal-bars span:nth-child(2) { height: 16px; }
.signal-bars span:nth-child(3) { height: 12px; }
.signal-bars span:nth-child(4) { height: 21px; }
.signal-bars span:nth-child(5) { height: 17px; }
.signal-bars.warning span { background-color: #e6a23c; }

.node-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.auth-column {
  min-width: 0;
  padding: 48px;
  display: flex;
  align-items: center;
  background-color: var(--el-bg-color);
  border-left: solid 1px var(--el-border-color);
}

.auth-column :deep(.auth-view) {
  width: 100%;
  max-width: 344px;
  margin: 0 auto;
}

.auth-column :deep(.auth-heading) {
  margin-bottom: 32px;
}

.auth-column :deep(.auth-heading h2) {
  margin: 0;
  font-size: 26px;
  line-height: 1.35;
}

.auth-column :deep(.auth-heading p) {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.auth-column :deep(.auth-form .el-form-item) {
  margin-bottom: 18px;
}

.auth-column :deep(.auth-form .el-input__wrapper) {
  min-height: 42px;
  border-radius: 5px;
}

.auth-column :deep(.auth-submit) {
  width: 100%;
  height: 42px;
  margin-top: 18px;
  border-radius: 5px;
}

.dark .platform-overview {
  background-color: #232323;
}

@media (max-width: 800px) {
  .welcome-page {
    height: auto;
    min-height: 100vh;
    min-height: 100dvh;
    overflow: auto;
  }

  .welcome-header {
    height: 58px;
    padding: 0 20px;
  }

  .brand-logo {
    width: 112px;
    height: 26px;
  }

  .brand-name {
    display: none;
  }

  .secure-state {
    display: none;
  }

  .welcome-main {
    min-height: calc(100vh - 58px);
    min-height: calc(100dvh - 58px);
    display: flex;
    flex-direction: column;
  }

  .platform-overview {
    min-height: 172px;
    padding: 30px 24px;
    align-items: center;
    border-bottom: solid 1px var(--el-border-color);
  }

  .overview-title h1 {
    margin-top: 10px;
    font-size: 28px;
  }

  .overview-title p {
    font-size: 13px;
  }

  .monitor-panel {
    display: none;
  }

  .auth-column {
    min-height: 540px;
    padding: 38px 24px 48px;
    align-items: flex-start;
    border-left: none;
  }
}

@media (max-width: 380px) {
  .welcome-header,
  .platform-overview,
  .auth-column {
    padding-left: 18px;
    padding-right: 18px;
  }
}
</style>
