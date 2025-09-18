<template>
  <div class="home-container">
    <h2 class="page-title">年度财报总览</h2>

    <el-row :gutter="20">
      <el-col
          v-for="report in reports"
          :key="report.id"
          :span="6"
      >
        <el-card
            shadow="hover"
            class="report-card"
            @click="goToDashboard(report.id)"
        >
          <div class="card-content">
            <h3 class="company-name">{{ report.company_name }}</h3>
            <p class="report-title">{{ report.title }}</p>
            <p class="report-year">年份：{{ report.year }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'

const router = useRouter()
const reports = ref([])

onMounted(async () => {
  try {
    const res = await http.get('/annualReports/getAll')
    reports.value = res.data
    console.log("获取到的年报数据:", reports.value)
  } catch (err) {
    console.error('获取年报数据失败:', err)
  }
})

function goToDashboard(id) {
  router.push({ path: '/Main/Dashboard', query: { id } })
}
</script>

<style scoped>
.home-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.report-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 12px;
  margin-top: 5px;
}

.report-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}

.card-content {
  text-align: center;
  padding: 10px 0;
}

.company-name {
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8px;
}

.report-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.report-year {
  font-size: 13px;
  color: #909399;
}
</style>