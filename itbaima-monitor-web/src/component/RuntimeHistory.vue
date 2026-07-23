<script setup>
import * as echarts from "echarts";
import {nextTick, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {defaultOption, doubleSeries, singleSeries} from "@/echarts";

const props = defineProps({
  data: Array,
  memory: Number
})

const cpuUsage = ref()
const memoryUsage = ref()
const networkUsage = ref()
const diskUsage = ref()
const charts = []
let resizeObserver

const localTimeLine = list => list.map(item => item.timestamp)
const numberValue = value => Number(value || 0)

function normalizeSeries(series, baseUnit) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const baseIndex = units.indexOf(baseUnit)
  const max = Math.max(...series.flat().map(numberValue), 0)
  let index = baseIndex
  let divisor = 1
  while (max / divisor >= 1024 && index < units.length - 1) {
    divisor *= 1024
    index++
  }
  while (max / divisor < 1 && max > 0 && index > 0) {
    divisor /= 1024
    index--
  }
  return {
    data: series.map(items => items.map(value => (numberValue(value) / divisor).toFixed(1))),
    unit: `${units[index]}/s`
  }
}

function updateCpuUsage(list) {
  const data = list.map(item => (numberValue(item.cpuUsage) * 100).toFixed(1))
  const option = defaultOption('CPU (%)', localTimeLine(list), {unit: '%', max: 100})
  singleSeries(option, 'CPU使用率', data, ['#409eff', '#79bbff66', '#409eff08'], 80)
  charts[0].setOption(option, true)
}

function updateMemoryUsage(list) {
  const data = list.map(item => props.memory ? (numberValue(item.memoryUsage) / props.memory * 100).toFixed(1) : 0)
  const option = defaultOption('内存 (%)', localTimeLine(list), {unit: '%', max: 100})
  singleSeries(option, '内存使用率', data, ['#67c23a', '#95d47566', '#67c23a08'], 85)
  charts[1].setOption(option, true)
}

function updateNetworkUsage(list) {
  const normalized = normalizeSeries([
    list.map(item => item.networkUpload),
    list.map(item => item.networkDownload)
  ], 'KB')
  const option = defaultOption(`网络 (${normalized.unit})`, localTimeLine(list), {
    unit: normalized.unit,
    legend: true,
    decimals: 1
  })
  doubleSeries(option, ['上传', '下载'], normalized.data, ['#e6a23c', '#409eff'])
  charts[2].setOption(option, true)
}

function updateDiskUsage(list) {
  const normalized = normalizeSeries([
    list.map(item => item.diskRead),
    list.map(item => item.diskWrite)
  ], 'MB')
  const option = defaultOption(`磁盘 (${normalized.unit})`, localTimeLine(list), {
    unit: normalized.unit,
    legend: true,
    decimals: 1
  })
  doubleSeries(option, ['读取', '写入'], normalized.data, ['#67c23a', '#409eff'])
  charts[3].setOption(option, true)
}

function updateCharts(list) {
  if(!list?.length || charts.length !== 4) return
  updateCpuUsage(list)
  updateMemoryUsage(list)
  updateNetworkUsage(list)
  updateDiskUsage(list)
}

onMounted(() => {
  const chartElements = [cpuUsage.value, memoryUsage.value, networkUsage.value, diskUsage.value]
  chartElements.forEach(element => charts.push(echarts.init(element)))
  resizeObserver = new ResizeObserver(() => charts.forEach(chart => chart.resize()))
  chartElements.forEach(element => resizeObserver.observe(element))
  nextTick(() => updateCharts(props.data))
})

watch(() => [props.data, props.memory], () => updateCharts(props.data), {deep: true})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  charts.forEach(chart => chart.dispose())
})
</script>

<template>
  <div class="charts">
    <div class="chart-item">
      <div class="chart-title">CPU 使用率</div>
      <div ref="cpuUsage" class="chart"></div>
    </div>
    <div class="chart-item">
      <div class="chart-title">内存使用率</div>
      <div ref="memoryUsage" class="chart"></div>
    </div>
    <div class="chart-item">
      <div class="chart-title">网络吞吐</div>
      <div ref="networkUsage" class="chart"></div>
    </div>
    <div class="chart-item">
      <div class="chart-title">磁盘 I/O</div>
      <div ref="diskUsage" class="chart"></div>
    </div>
  </div>
</template>

<style scoped>
.charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.chart-item {
  min-width: 0;
}

.chart-title {
  color: var(--el-text-color-primary);
  font-size: 15px;
  font-weight: bold;
}

.chart {
  width: 100%;
  height: 220px;
}

@media (max-width: 700px) {
  .charts {
    grid-template-columns: 1fr;
  }
}
</style>
