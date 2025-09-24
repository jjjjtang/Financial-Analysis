<template>
  <div class="market-container">
    <h2>金融信息概览</h2>

    <!-- 第一行：基本信息 + 实时行情 -->
    <div class="top-section">
      <!-- 基本信息 -->
      <el-card class="info-card" shadow="hover">
        <h3>基本信息</h3>
        <p><strong>公司名称：</strong> {{ basicInfo.name }}</p>
        <p><strong>市值：</strong> {{ basicInfo.marketCap }} 亿元</p>
        <p><strong>行业：</strong> {{ basicInfo.industry }}</p>
        <p><strong>每股收益：</strong> {{ basicInfo.eps }}</p>
        <p><strong>市盈率(PE)：</strong> {{ basicInfo.pe }}</p>
        <p><strong>市净率(PB)：</strong> {{ basicInfo.pb }}</p>
      </el-card>

      <!-- 实时行情 -->
      <el-card class="quote-card" shadow="hover">
        <h3>实时行情</h3>
        <p><strong>当前价格：</strong> {{ realtime.price }} 元</p>
        <p><strong>涨跌幅：</strong> {{ realtime.change }}%</p>
        <div ref="priceChart" class="chart-box"></div>
      </el-card>
    </div>

    <!-- 第二行：高频序列展示 -->
    <el-card class="series-card" shadow="hover">
      <h3>高频金融序列</h3>
      <div ref="seriesChart" class="chart-box"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 模拟基本金融信息
const basicInfo = ref({
  name: '某科技股份有限公司',
  marketCap: 3500,
  industry: '信息技术',
  eps: 4.25,
  pe: 23.5,
  pb: 5.2
})

// 模拟实时行情
const realtime = ref({
  price: 128.75,
  change: 2.34
})

// 模拟高频序列数据，这些都是暂时性验证的后期还需做更改
const seriesData = ref([
  { time: '09:30', price: 127 },
  { time: '09:31', price: 127.5 },
  { time: '09:32', price: 128.1 },
  { time: '09:33', price: 128.75 },
  { time: '09:34', price: 128.5 }
])

const priceChart = ref(null)
const seriesChart = ref(null)

// 初始化图表
onMounted(() => {
  // 实时行情图
  const chart1 = echarts.init(priceChart.value)
  chart1.setOption({
    title: { text: '分时价格走势', left: 'center' },
    xAxis: {
      type: 'category',
      data: seriesData.value.map(d => d.time)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '价格',
      type: 'line',
      data: seriesData.value.map(d => d.price)
    }]
  })

  // 高频序列图（可换成成交量等）
  const chart2 = echarts.init(seriesChart.value)
  chart2.setOption({
    title: { text: '高频序列价格变化' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: seriesData.value.map(d => d.time)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '价格',
      type: 'bar',
      data: seriesData.value.map(d => d.price)
    }]
  })
})
</script>

<style scoped>
.market-container {
  padding: 20px;
  background: #fff;
}

.top-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.info-card, .quote-card {
  flex: 1;
}

.series-card {
  margin-top: 20px;
}

.chart-box {
  height: 300px;
  margin-top: 10px;
}
</style>
