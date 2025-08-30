<template>
  <div class="analysis-container">
    <h2>年报分析</h2>

    <!-- 模型选择 -->
    <div class="model-selection">
      <el-radio-group v-model="selectedModel">
        <el-radio-button label="Hithink">Hithink</el-radio-button>
        <el-radio-button label="Deepseek">Deepseek</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Deepseek 子功能选择 -->
    <div v-if="selectedModel==='Deepseek'" class="deepseek-buttons" style="margin-top:10px;">
      <el-button
          type="primary"
          :plain="analysisType!=='summary'"
          @click="analysisType='summary'"
      >
        年报总体分析
      </el-button>
      <el-button
          type="primary"
          :plain="analysisType!=='synopsis'"
          @click="analysisType='synopsis'"
      >
        年报要点分析
      </el-button>
    </div>

    <!-- PDF 文件选择 -->
    <div style="margin-top:15px;">
      <el-select
          v-model="selectedPdf"
          placeholder="选择PDF文件"
          style="width:100%;"
      >
        <el-option
            v-for="file in pdfFiles"
            :key="file.path"
            :label="file.name"
            :value="file.path"
        />
      </el-select>
    </div>

    <!-- 分析按钮 -->
    <el-button
        type="primary"
        style="margin-top:10px;"
        :disabled="!selectedPdf"
        @click="fetchAnalysis"
    >
      开始分析
    </el-button>

    <!-- 分析结果显示 -->
    <div class="result-box" v-if="analysisResult">
      <h3>分析结果</h3>
      <pre>{{ analysisResult }}</pre>
    </div>

    <el-empty v-else description="暂无分析结果" />
  </div>
</template>

<script setup>
import {ref} from 'vue'
import http from '@/api/http'

const selectedModel = ref('Hithink')
const analysisType = ref('summary') // Deepseek 默认总体分析
const selectedPdf = ref('')
const pdfFiles = ref([
  {name: '平安银行 2021 年报', path: 'annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf'},
  {name: '平安银行 2022 年报', path: 'annualReportTools/annualFiles/2022/pdf_Format/000001_平安银行_2022.pdf'}
])
const analysisResult = ref('')

const fetchAnalysis = async () => {
  if (!selectedPdf.value) return

  analysisResult.value = '分析中，请稍候...'

  try {
    let res
    if (selectedModel.value === 'Hithink') {
      res = await http.post('/hithink/analysis', {file_path: selectedPdf.value}, {
        headers: {'Content-Type': 'application/json'},
        timeout: 300000
      })
      analysisResult.value = res.data.reply
    } else if (selectedModel.value === 'Deepseek') {
      const url = analysisType.value === 'summary' ? '/deepseek/analysis' : '/deepseek/synopsis'
      res = await http.post(url, {file_path: selectedPdf.value}, {
        headers: {'Content-Type': 'application/json'},
        timeout: 300000
      })
      // 如果是要点分析，将对象转换为可读字符串
      if (analysisType.value === 'synopsis') {
        analysisResult.value = Object.entries(res.data).map(([key, val]) => `${key}：${val}`).join('\n')
      } else {
        analysisResult.value = res.data.reply
      }
    }
  } catch (err) {
    console.error('分析失败', err)
    analysisResult.value = '分析失败，请稍后重试'
  }
}
</script>

<style scoped>
.analysis-container {
  padding: 20px;
  background: #fff;
  min-height: 100%;
}

.model-selection {
  margin-bottom: 10px;
}

.deepseek-buttons {
  display: flex;
  gap: 10px;
}

.result-box {
  margin-top: 20px;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
}
</style>
