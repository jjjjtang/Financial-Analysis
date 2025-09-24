<template>
  <div class="p-6 bg-gray-50 min-h-screen flex items-center justify-center">
    <el-card class="w-full max-w-6xl shadow-lg rounded-2xl border border-gray-200">
      <!-- 卡片标题 -->
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold text-gray-700">历史K线数据展示</h2>
          <el-tag type="success">历史行情</el-tag>
        </div>
      </template>

      <!-- K线图 -->
      <div class="chart-container">
        <div ref="chartRef" class="chart-box"></div>
      </div>

      <!-- 表格 -->
      <el-table :data="tableData" border stripe style="margin-top: 20px">
        <el-table-column prop="date" label="日期" align="center" />
        <el-table-column prop="open" label="开盘价" align="center" />
        <el-table-column prop="close" label="收盘价" align="center" />
        <el-table-column prop="low" label="最低价" align="center" />
        <el-table-column prop="high" label="最高价" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";
import * as echarts from "echarts";

const chartRef = ref(null);

// ✅ 静态数据
const tableData = [
  { date: "2025-09-01", open: 2320, close: 2350, low: 2300, high: 2360 },
  { date: "2025-09-02", open: 2350, close: 2400, low: 2340, high: 2420 },
  { date: "2025-09-03", open: 2400, close: 2380, low: 2370, high: 2430 },
  { date: "2025-09-04", open: 2380, close: 2450, low: 2360, high: 2460 },
  { date: "2025-09-05", open: 2450, close: 2430, low: 2420, high: 2480 },
  { date: "2025-09-06", open: 2430, close: 2500, low: 2410, high: 2520 },
  { date: "2025-09-07", open: 2500, close: 2550, low: 2490, high: 2560 }
];

const dates = tableData.map((item) => item.date);
const values = tableData.map((item) => [item.open, item.close, item.low, item.high]);

onMounted(async () => {
  await nextTick(); // 确保 DOM 渲染完成

  if (chartRef.value) {
    const chart = echarts.init(chartRef.value);

    const option = {
      title: {
        text: "股票历史K线走势",
        left: "center"
      },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross" }
      },
      xAxis: {
        type: "category",
        data: dates,
        boundaryGap: true
      },
      yAxis: {
        scale: true
      },
      grid: {
        left: "5%",
        right: "5%",
        top: "15%",
        bottom: "10%"
      },
      series: [
        {
          type: "candlestick",
          data: values,
          itemStyle: {
            color: "#ef4444", // 红涨
            color0: "#22c55e", // 绿跌
            borderColor: "#ef4444",
            borderColor0: "#22c55e"
          }
        }
      ]
    };

    chart.setOption(option);
    window.addEventListener("resize", () => chart.resize());
  }
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 420px;
  margin-bottom: 20px;
}
.chart-box {
  width: 100%;
  height: 100%;
  border: 1px solid #ddd;
  background-color: #fafafa;
}
</style>