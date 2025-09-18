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

      <!-- 模型选择 -->
      <el-radio-group v-model="selectedModel" style="margin-bottom: 10px;">
        <el-radio-button label="Hithink">Hithink</el-radio-button>
        <el-radio-button label="Deepseek">Deepseek</el-radio-button>
      </el-radio-group>

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
          <svg t="1758187478669" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
               width="20" height="20">
            <path d="M368.896 192H224a32 32 0 0 0-32 32v137.888a32 32 0 0 0 64 0V256h112.896a32 32 0 0 0 0-64zM784.864 192H640a32 32 0 1 0 0 64h112.864v105.888a32 32 0 1 0 64 0V224a32 32 0 0 0-32-32zM368.896 777.92H256V672a32 32 0 1 0-64 0v137.92a32 32 0 0 0 32 32h144.896a32 32 0 1 0 0-64zM784.864 640a32 32 0 0 0-32 32v105.92H640a32 32 0 1 0 0 64h144.864a32 32 0 0 0 32-32V672a32 32 0 0 0-32-32z" fill="#707070"></path>
            <path d="M912 48h-800c-35.296 0-64 28.704-64 64v800c0 35.296 28.704 64 64 64h800c35.296 0 64-28.704 64-64v-800c0-35.296-28.704-64-64-64z m-800 864v-800h800l0.064 800H112z" fill="#707070"></path>
          </svg>
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
const selectedModel = ref('Hithink')
const loading = ref(false)
const dialogVisible = ref(false)

onMounted(async () => {
  // 优先从路由获取id，如果没有就尝试从本地存储读取
  let id = route.query.id || localStorage.getItem('reportId')
  if (!id) return

  // 如果是通过路由进入，保存到本地存储
  if (route.query.id) {
    localStorage.setItem('reportId', id)
  }

  try {
    const res = await http.get('/annualReports/getById', { params: { id } })
    report.value = res.data
  } catch (err) {
    console.error('获取年报详情失败:', err)
  }
})

// 发送消息
async function sendMessage() {
  if (!inputMessage.value.trim() || !report.value) return
  const question = inputMessage.value
  inputMessage.value = ''
  messages.value.push({ role: '用户', content: question })

  loading.value = true
  const thinkingMsgIndex = messages.value.push({ role: 'AI', content: '思考中...' }) - 1

  try {
    let res
    if (selectedModel.value === 'Hithink') {
      res = await http.post(
          '/hithink/financialAssistant',
          { file_path: report.value.pdf_url, question },
          { headers: { 'Content-Type': 'application/json' }, timeout: 900000 }
      )
    } else {
      res = await http.post(
          '/deepseek/analysis',
          { file_path: report.value.pdf_url, message: question },
          { headers: { 'Content-Type': 'application/json' }, timeout: 900000 }
      )
    }

    messages.value[thinkingMsgIndex].content = md.render(res.data.reply || '（无返回内容）')
  } catch (err) {
    messages.value[thinkingMsgIndex].content = '接口请求失败，请稍后再试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 下载 PDF
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

.dialog-close-btn {
  margin-left: auto;
}
</style>