<template>
  <div class="dashboard-container">
    <!-- 左侧财报展示 -->
    <div class="left-panel">
      <div class="report-header">
        <h3 class="section-title">财报详情</h3>
        <div class="report-info">
          <span class="report-title">
            {{ report?.company_name }} - {{ report?.title }}
          </span>
          <el-button
              v-if="report"
              type="primary"
              size="small"
              @click="downloadReport"
          >
            下载PDF
          </el-button>
        </div>
      </div>

      <div class="report-result" v-if="report">
        <iframe
            :src="report.link"
            class="pdf-viewer"
            frameborder="0"
        ></iframe>
      </div>
    </div>

    <!-- 右侧 AI 问答界面 -->
    <div class="right-panel">
      <h3>AI 财报问答</h3>

      <!-- 模型选择 下拉框 -->
      <el-select v-model="selectedModel" placeholder="选择模型" style="margin-bottom: 10px; width: 100%;">
        <el-option
            v-for="model in models"
            :key="model.value"
            :label="model.label"
            :value="model.value"
        />
      </el-select>

      <!-- 聊天框 -->
      <div class="chat-container">
        <div class="chat-box">
          <div
              class="chat-message"
              v-for="(msg, index) in messages"
              :key="index"
          >
            <strong>{{ msg.role }}：</strong>
            <div v-if="msg.role === 'AI'" v-html="msg.content"></div>
            <div v-else>{{ msg.content }}</div>
          </div>
        </div>

        <!-- 放大按钮 -->
        <el-button
            circle
            size="mini"
            class="expand-btn"
            @click="dialogVisible = true"
            title="放大查看"
        >
          🔍
        </el-button>
      </div>

      <el-input
          type="textarea"
          v-model="inputMessage"
          placeholder="请输入你的问题"
          rows="3"
          :disabled="loading"
          @keydown.enter.prevent="sendMessage"
      />
      <el-button
          type="primary"
          @click="sendMessage"
          style="margin-top: 10px;"
          :disabled="!report || !inputMessage.trim() || loading"
      >
        {{ loading ? '思考中...' : '发送' }}
      </el-button>

      <!-- 返回首页按钮 -->
      <el-button
          type="info"
          plain
          style="margin-top: 10px;"
          @click="goHome"
      >
        返回首页
      </el-button>
    </div>

    <!-- Dialog 放大聊天框 -->
    <el-dialog
        v-model="dialogVisible"
        width="70vw"
        top="5vh"
        custom-class="full-chat-dialog"
        :close-on-click-modal="false"
    >
      <template #title>
        <div class="dialog-title">
          <span>AI 聊天内容</span>
        </div>
      </template>

      <div class="dialog-chat-box">
        <div
            class="chat-message"
            v-for="(msg, index) in messages"
            :key="'dialog-' + index"
        >
          <strong>{{ msg.role }}：</strong>
          <div v-if="msg.role === 'AI'" v-html="msg.content"></div>
          <div v-else>{{ msg.content }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/api/http'
import MarkdownIt from 'markdown-it'

const route = useRoute()
const router = useRouter()
const md = new MarkdownIt()

const report = ref(null)
const messages = ref([])
const inputMessage = ref('')
const selectedModel = ref('Hithink') // 默认模型
const loading = ref(false)
const dialogVisible = ref(false)

// 下拉框模型列表，只有两个实际模型，其他虚拟模型仅显示
const models = [
  { label: 'Hithink', value: 'Hithink' },
  { label: 'Deepseek', value: 'Deepseek' },
  { label: 'FinBot', value: 'FinBot' },
  { label: 'SmartFinance', value: 'SmartFinance' },
  { label: 'AlphaAI', value: 'AlphaAI' }
]

onMounted(async () => {
  let id = route.query.id || localStorage.getItem('reportId')
  if (!id) return
  if (route.query.id) localStorage.setItem('reportId', id)

  try {
    const res = await http.get('/annualReports/getById', { params: { id } })
    report.value = res.data
  } catch (err) {
    console.error('获取年报详情失败:', err)
  }
})

async function sendMessage() {
  if (!inputMessage.value.trim() || !report.value) return
  const question = inputMessage.value
  inputMessage.value = ''
  messages.value.push({ role: '用户', content: question })

  loading.value = true
  const thinkingMsgIndex = messages.value.push({ role: 'AI', content: '思考中...' }) - 1

  try {
    let res
    // 仅实际模型才请求接口，虚拟模型直接返回提示
    if (selectedModel.value === 'Hithink') {
      res = await http.post(
          '/hithink/financialAssistant',
          { file_path: report.value.pdf_url, question },
          { headers: { 'Content-Type': 'application/json' }, timeout: 900000 }
      )
      messages.value[thinkingMsgIndex].content = md.render(res.data.reply || '（无返回内容）')
    } else if (selectedModel.value === 'Deepseek') {
      res = await http.post(
          '/deepseek/analysis',
          { file_path: report.value.pdf_url, message: question },
          { headers: { 'Content-Type': 'application/json' }, timeout: 900000 }
      )
      messages.value[thinkingMsgIndex].content = md.render(res.data.reply || '（无返回内容）')
    } else {
      messages.value[thinkingMsgIndex].content = `【${selectedModel.value}】模型为虚拟模型，暂不支持实际查询`
    }
  } catch (err) {
    messages.value[thinkingMsgIndex].content = '接口请求失败，请稍后再试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function downloadReport() {
  if (report.value?.link) window.open(report.value.link, '_blank')
}

function goHome() {
  router.push('/home')
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
  display: flex;
  flex-direction: column;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
}

.report-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.report-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.pdf-viewer {
  width: 100%;
  height: 720px;
  border: none;
}

.right-panel {
  width: 400px;
  padding: 20px;
  background-color: #fafafa;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chat-container {
  position: relative;
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

.expand-btn {
  position: absolute;
  top: 5px;
  right: 5px;
}

.full-chat-dialog .el-dialog__body {
  padding: 0;
}

.dialog-chat-box {
  max-height: 70vh;
  overflow-y: auto;
  padding: 15px;
  background-color: #fff;
}

.dialog-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
