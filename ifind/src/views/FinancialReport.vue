<template>
  <div class="summary-container">
    <h2>财报摘要提取结果</h2>

    <!-- 模拟多段提炼内容 -->
    <el-card
        v-for="(item, index) in summaryList"
        :key="index"
        class="summary-card"
        shadow="hover"
    >
      <div class="summary-title">要点 {{ index + 1 }}</div>
      <div class="summary-content">{{ item }}</div>
    </el-card>

    <el-empty v-if="summaryList.length === 0" description="暂无数据，请稍后再试" />
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 模拟后端返回的提炼段落内容，都是静态数据根据后面再做更改
const summaryList = ref([
  "公司2025年第二季度营收达到150亿元，同比增长12.5%。",
  "净利润为28亿元，环比增长6.2%。",
  "公司表示海外市场业务增长迅速，占比首次超过30%。",
  "研发投入持续加大，占总营收比例达8.7%。",
  "董事会宣布将在下一季度实施股东分红政策。"
])

// TODO：未来这里替换为 axios 请求
// axios.get('/report-summary?id=xxx').then(res => {
//   summaryList.value = res.data.summary
// })
</script>

<style scoped>
.summary-container {
  padding: 20px;
  background: #fff;
  min-height: 100%;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-title {
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.summary-content {
  color: #606266;
  line-height: 1.6;
}
</style>
