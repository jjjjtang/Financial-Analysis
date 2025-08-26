<template>
  <div class="dashboard-container">
    <!-- 左侧财报信息 -->
    <div class="left-panel">
      <h3>财报主要内容</h3>
      <el-table :data="reportData" stripe style="width: 100%">
        <el-table-column prop="quarter" label="季度" width="120" />
        <el-table-column prop="revenue" label="营收 (亿元)" />
        <el-table-column prop="profit" label="利润 (亿元)" />
        <el-table-column prop="growth" label="同比增长 (%)" />
      </el-table>

      <div ref="chart" class="chart-container"></div>
    </div>

    <!-- 右侧 AI 问答界面 -->
    <div class="right-panel">
      <h3>AI 财报问答</h3>
      <div class="chat-box">
        <div class="chat-message user" v-for="(msg, index) in messages" :key="index">
          <strong>{{ msg.role }}：</strong>{{ msg.content }}
        </div>
      </div>

      <el-input
          type="textarea"
          v-model="inputMessage"
          placeholder="请输入你的问题（待接入后端）"
          rows="3"
      />
      <el-button type="primary" @click="sendMessage" style="margin-top: 10px;">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 模拟财报数据。上面预留了4个数据类型后续根据实际需要进行更改，我这里预设了静态数据进行验证能否正常运行




const reportData = ref([
  { quarter: '2025 Q1', revenue: 120, profit: 25, growth: 12.3 },
  { quarter: '2025 Q2', revenue: 135, profit: 30, growth: 10.5 },
  { quarter: '2025 Q3', revenue: 150, profit: 32, growth: 11.2 },
  { quarter: '2025 Q4', revenue: 165, profit: 36, growth: 12.8 }
])

// 模拟聊天记录
const messages = ref([
  { role: '用户', content: '公司本季度营收怎么样？' },
  { role: 'AI', content: '本季度营收为165亿元，同比增长12.8%。' }
])

const inputMessage = ref('')

// 发送消息（预留方法）   这里对接后端数据也是我先预设检验能否正常启动
function sendMessage() {
  if (!inputMessage.value.trim()) return

  // 添加到消息列表中
  messages.value.push({ role: '用户', content: inputMessage.value })

  // TODO: 调用后端 API 获取回复
  messages.value.push({ role: 'AI', content: '（AI 回复待接入后端）' })

  inputMessage.value = ''
}

// 初始化图表
const chart = ref(null)
onMounted(() => {
  const myChart = echarts.init(chart.value)
  const option = {
    title: { text: '季度营收走势' },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: reportData.value.map(item => item.quarter)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '营收',
        type: 'bar',
        data: reportData.value.map(item => item.revenue)
      }
    ]
  }
  myChart.setOption(option)
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  gap: 20px;
  height: 100%;
}

/* 左侧财报区域 */
.left-panel {
  flex: 1;
  padding: 20px;
  background-color: #fff;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-container {
  height: 300px;
  margin-top: 20px;
}

/* 右侧 AI 问答区域 */
.right-panel {
  width: 400px;
  padding: 20px;
  background-color: #fafafa;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  background: #fff;
  border: 1px solid #dcdfe6;
  padding: 10px;
  height: 300px;
}

.chat-message {
  margin-bottom: 10px;
  line-height: 1.6;
}

.user {
  text-align: left;
}

.ai {
  text-align: right;
}
</style>
