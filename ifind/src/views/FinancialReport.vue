<template>
  <div class="analysis-container">
    <!-- 页面标题 -->
    <h2 class="page-title">年度财报分析</h2>

    <!-- 当前分析的年报信息 -->
    <el-card class="report-info-card" shadow="hover" v-if="report">
      <div class="report-info">
        <span class="company-name">{{ report.company_name }}</span>
        <span class="report-year">({{ report.year }} 年报)</span>
      </div>
    </el-card>

    <!-- 模型选择卡片 -->
    <el-row :gutter="20" class="model-row">
      <el-col :span="12">
        <el-card shadow="hover" class="model-card">
          <div class="model-header">
            <h3>Hithink 分析</h3>
            <el-switch
                v-model="hithinkType"
                active-text="要点分析"
                inactive-text="总体分析"
            />
          </div>
          <el-button
              type="primary"
              :loading="loading && selectedModel==='Hithink'"
              style="margin-top:15px"
              @click="fetchAnalysis('Hithink')"
          >
            开始分析
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover" class="model-card">
          <div class="model-header">
            <h3>Deepseek 分析</h3>
            <el-switch
                v-model="deepseekType"
                active-text="要点分析"
                inactive-text="总体分析"
            />
          </div>
          <el-button
              type="primary"
              :loading="loading && selectedModel==='Deepseek'"
              style="margin-top:15px"
              @click="fetchAnalysis('Deepseek')"
          >
            开始分析
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析结果展示 -->
    <el-card class="result-card" shadow="hover" v-if="analysisResult">
      <h3>分析结果</h3>
      <el-scrollbar style="max-height:400px;">
        <pre>{{ analysisResult }}</pre>
      </el-scrollbar>
    </el-card>

    <el-empty v-else description="暂无分析结果" style="margin-top: 20px;" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/api/http'

const selectedModel = ref('Hithink')
const hithinkType = ref(false)   // false = 总体分析, true = 要点分析
const deepseekType = ref(false)
const report = ref(null)
const analysisResult = ref('')
const loading = ref(false)

// 页面加载时获取本地 reportId
onMounted(async () => {
  const id = localStorage.getItem('reportId')
  if (!id) {
    console.error('未找到本地存储的年报ID')
    return
  }

  try {
    const res = await http.get('/annualReports/getById', { params: { id } })
    report.value = res.data
  } catch (err) {
    console.error('获取年报详情失败:', err)
  }
})

// 分析方法
const fetchAnalysis = async (model) => {
  if (!report.value) return
  selectedModel.value = model
  analysisResult.value = '分析中，请稍候...'
  loading.value = true

  try {
    let res
    const type = model === 'Hithink' ? hithinkType.value : deepseekType.value

    if (model === 'Hithink') {
      res = await http.post('/hithink/financialAssistant',
          { file_path: report.value.pdf_url, question: '', type: type ? 'synopsis' : 'summary' },
          { headers: {'Content-Type':'application/json'}, timeout:300000 }
      )
      analysisResult.value = res.data.reply || '（无返回内容）'
    } else {
      const url = type ? '/deepseek/synopsis' : '/deepseek/analysis'
      res = await http.post(url, { file_path: report.value.pdf_url }, { headers: {'Content-Type':'application/json'}, timeout:600000 })
      console.log(res.data)
      if (type) {
        analysisResult.value = Object.entries(res.data).map(([key,val])=>`${key}：${val}`).join('\n')
      } else {
        analysisResult.value = res.data.reply
      }
    }
  } catch (err) {
    console.error('分析失败', err)
    analysisResult.value = '分析失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.analysis-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

/* 年报信息卡片 */
.report-info-card {
  margin-bottom: 20px;
  padding: 15px 20px;
}

.report-info {
  font-size: 16px;
  color: #606266;
}

.company-name {
  font-weight: 600;
  color: #409EFF;
  margin-right: 5px;
}

.report-year {
  color: #909399;
}

/* 模型卡片 */
.model-row {
  margin-bottom: 20px;
}

.model-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 20px;
  transition: all 0.3s;
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

.model-header {
  justify-content: space-between;
  width: 100%;
  align-items: center;
}

.result-card {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>