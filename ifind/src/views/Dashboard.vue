<template>
  <div class="dashboard-container">
    <!-- 左侧财报查询 -->
    <div class="left-panel">
      <h3>财报查询</h3>
      <div class="query-form">
        <el-input v-model="companyCode" placeholder="公司代码" style="flex:1; margin-right:5px;" />
        <el-input v-model="year" placeholder="年份" style="flex:1; margin-right:5px;" />
        <el-input v-model="reportId" placeholder="报表ID" style="flex:1;" />
        <el-button type="primary" @click="fetchReport" style="margin-left:5px;">查询</el-button>
      </div>

      <div class="report-result" v-if="reportList.length">
        <div v-for="item in reportList" :key="item.id" class="report-item">
          <p><strong>{{ item.company_name }}</strong> - {{ item.title }}：
            <a :href="item.link" target="_blank">{{ item.link }}</a>
          </p>
        </div>
      </div>
    </div>

    <!-- 右侧 AI 问答界面 -->
    <div class="right-panel">
      <h3>AI 财报问答</h3>

      <!-- 模型选择滑块 -->
      <el-radio-group v-model="selectedModel" style="margin-bottom: 10px;">
        <el-radio-button label="Hithink">Hithink</el-radio-button>
        <el-radio-button label="Deepseek">Deepseek</el-radio-button>
      </el-radio-group>

      <!-- PDF 文件选择 -->
      <el-select
          v-model="selectedPdf"
          placeholder="选择PDF文件"
          style="width: 100%; margin-bottom: 10px;"
      >
        <el-option
            v-for="file in pdfFiles"
            :key="file.path"
            :label="file.name"
            :value="file.path"
        />
      </el-select>

      <div class="chat-box">
        <div
            class="chat-message user"
            v-for="(msg, index) in messages"
            :key="index"
        >
          <strong>{{ msg.role }}：</strong>{{ msg.content }}
        </div>
      </div>

      <el-input
          type="textarea"
          v-model="inputMessage"
          placeholder="请输入你的问题"
          rows="3"
      />
      <el-button
          type="primary"
          @click="sendMessage"
          style="margin-top: 10px;"
          :disabled="!selectedPdf || !inputMessage.trim()"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as echarts from 'echarts'
import http from '@/api/http'

// 左侧查询输入
const companyCode = ref('')
const year = ref('')
const reportId = ref('')

// 查询结果
const reportList = ref([])

// AI 问答
const messages = ref([])
const inputMessage = ref('')
const selectedModel = ref('Hithink')
const pdfFiles = ref([
  {name: '平安银行 2021 年报', path: 'annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf'},
  {name: '平安银行 2022 年报', path: 'annualReportTools/annualFiles/2022/pdf_Format/000001_平安银行_2022.pdf'}
])
const selectedPdf = ref('')

// 查询年报
async function fetchReport() {
  try {
    let res
    if (!companyCode.value && !year.value && !reportId.value) {
      // 全空，获取所有年报
      res = await http.get('/annualReports/getAll')
      reportList.value = res.data.map(r => ({
        company_name: r.company_name,
        title: r.title,
        link: r.link,
        pdf_url: r.pdf_url,
        id: r.id
      }))
    } else if (reportId.value.trim()) {
      // 根据 id 查询
      res = await http.get('/annualReports/getById', { params: { id: reportId.value } })
      reportList.value = [{
        company_name: res.data.company_name,
        title: res.data.title,
        link: res.data.link,
        pdf_url: res.data.pdf_url,
        id: res.data.id
      }]
    } else if (companyCode.value.trim() && year.value.trim()) {
      // 根据 company_code + year 查询
      res = await http.get('/annualReports/getByCompanyCodeAndYear', {
        params: { company_code: companyCode.value, year: year.value }
      })
      reportList.value = [{
        company_name: res.data.company_name,
        title: res.data.title,
        link: res.data.link,
        pdf_url: res.data.pdf_url,
        id: res.data.id
      }]
    } else {
      reportList.value = []
      alert('请完整填写查询条件')
    }

    // 自动更新右侧 PDF 下拉列表
    pdfFiles.value = reportList.value.map(r => ({
      name: `${r.company_name} - ${r.title}`,
      path: r.pdf_url
    }))
    selectedPdf.value = '' // 清空选择
  } catch (err) {
    console.error('查询失败', err)
    reportList.value = []
  }
}

// 发送消息
async function sendMessage() {
  if (!inputMessage.value.trim() || !selectedPdf.value) return
  messages.value.push({role: '用户', content: inputMessage.value})

  try {
    let res
    if (selectedModel.value === 'Hithink') {
      res = await http.post('/hithink/financialAssistant', {
        file_path: selectedPdf.value,
        question: inputMessage.value
      }, {
        headers: {'Content-Type': 'application/json'},
        timeout: 300000
      })
      messages.value.push({role: 'AI', content: res.data.reply})
    } else if (selectedModel.value === 'Deepseek') {
      res = await http.post('/deepseek/analysis', {
        file_path: selectedPdf.value,
        message: inputMessage.value
      }, {
        headers: {'Content-Type': 'application/json'},
        timeout: 300000
      })
      messages.value.push({role: 'AI', content: res.data.reply})
    }
  } catch (err) {
    console.error('AI 接口请求失败:', err)
    messages.value.push({role: 'AI', content: '接口请求失败，请稍后再试'})
  }

  inputMessage.value = ''
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  gap: 20px;
  height: 100%;
}

.left-panel {
  flex: 1;
  padding: 20px;
  background-color: #fff;
  overflow-y: auto;
}

.query-form {
  display: flex;
  margin-bottom: 10px;
}

.report-result {
  margin-top: 20px;
}

.report-item {
  margin-bottom: 10px;
}

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
