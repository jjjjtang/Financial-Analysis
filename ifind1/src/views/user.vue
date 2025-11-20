<template>
  <div class="dashboard-container">
    <!-- 左侧栏 -->
    <div class="sidebar">
      <div class="company-info">
        <img src="../assets/logo.svg" alt="公司头像" class="company-logo" />
        <h3 class="company-name">星辰科技股份有限公司</h3>
      </div>
      <el-menu default-active="stock" class="menu" @select="handleMenuSelect">
        <el-menu-item index="stock">财智管家</el-menu-item>
        <el-menu-item index="pdfai">智能财报助手</el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="content">
      <!-- 股票仓库 -->
      <div v-if="activeMenu==='stock'" class="stock-section">
        <el-row :gutter="20" class="overview-row">
          <el-col :span="8">
            <el-card class="overview-card" shadow="hover">
              <h3>总市值</h3>
              <p>{{ totalMarketValue }} 亿</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="overview-card" shadow="hover">
              <h3>平均涨跌幅</h3>
              <p :style="{ color: avgChange>=0 ? 'red':'green' }">{{ avgChange>=0?'+':'' }}{{ avgChange }}%</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="overview-card" shadow="hover">
              <h3>持仓股票数量</h3>
              <p>{{ stockList.length }} 支</p>
            </el-card>
          </el-col>
        </el-row>

        <el-form inline style="margin-bottom:20px">
          <el-form-item>
            <el-input v-model="newStockCode" placeholder="股票代码"></el-input>
          </el-form-item>
          <el-form-item>
            <el-input v-model="newStockName" placeholder="股票名称"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="success" @click="addStock">新增股票</el-button>
          </el-form-item>
        </el-form>

        <el-input
            v-model="searchQuery"
            placeholder="输入股票代码或名称搜索"
            prefix-icon="el-icon-search"
            class="search-box"
            clearable
        ></el-input>

        <el-table :data="filteredStocks" highlight-current-row @row-click="selectStock" style="width:100%" row-key="code" :row-class-name="tableRowClass">
          <el-table-column prop="code" label="股票代码" width="120"/>
          <el-table-column prop="name" label="名称" width="150"/>
          <el-table-column prop="price" label="当前价格" width="120"/>
          <el-table-column label="涨跌幅">
            <template #default="{ row }">
              <span :style="{ color: row.change>=0?'red':'green' }">
                {{ row.change>=0?'+':'' }}{{ row.change }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="primary" size="mini" @click.stop="selectStock(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="selectedStock" class="chart-container">
          <el-card shadow="hover" class="stock-detail-card">
            <h3>{{ selectedStock.name }} ({{ selectedStock.code }}) 详细信息</h3>
            <div class="stock-info">
              <span>当前价格: {{ selectedStock.price }}</span>
              <span :style="{ color: selectedStock.change>=0?'red':'green' }">涨跌幅: {{ selectedStock.change>=0?'+':'' }}{{ selectedStock.change }}%</span>
              <span>最高价: {{ Math.max(...selectedStock.history) }}</span>
              <span>最低价: {{ Math.min(...selectedStock.history) }}</span>
            </div>
            <v-chart :option="chartOption" autoresize style="height:300px; margin-top:20px"/>
          </el-card>
        </div>
      </div>

      <!-- PDF AI 分析 -->
      <div v-if="activeMenu==='pdfai'" class="pdfai-section">
        <!-- 右上角按钮 -->
        <div class="top-right-btns">
          <el-button type="warning" size="small" @click="changePassword">修改密码</el-button>
          <el-button type="danger" size="small" @click="logout">退出登录</el-button>
        </div>

        <h2>PDF AI 分析</h2>

        <!-- 上传 PDF -->
        <el-upload
            class="upload-demo"
            drag
            accept=".pdf"
            :auto-upload="false"
            :file-list="fileList"
            @change="handleUploadChange"
        >
          <i class="el-icon-upload" />
          <div class="el-upload__text">将 PDF 文件拖到此处，或点击上传</div>
          <template #tip>
            <div class="el-upload__tip">只支持 PDF 文件</div>
          </template>
        </el-upload>

        <!-- 已上传 PDF 选择 -->
        <el-form inline style="margin-top:20px">
          <el-form-item label="选择 PDF">
            <el-select v-model="selectedPdf" placeholder="请选择 PDF">
              <el-option
                  v-for="item in uploadedPdfs"
                  :key="item"
                  :label="item"
                  :value="item"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="downloadPdf">下载 PDF</el-button>
          </el-form-item>
        </el-form>

        <!-- 模型选择 -->
        <el-row :gutter="20" class="model-row">
          <el-col :span="12">
            <el-card class="model-card">
              <div class="model-header">
                <h3>Hithink 分析</h3>
                <el-switch v-model="hithinkType" active-text="要点分析" inactive-text="总体分析"/>
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
            <el-card class="model-card">
              <div class="model-header">
                <h3>Deepseek 分析</h3>
                <el-switch v-model="deepseekType" active-text="要点分析" inactive-text="总体分析"/>
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
        <el-card v-if="analysisResult" class="result-card">
          <h3>分析结果</h3>
          <el-scrollbar style="max-height:400px;">
            <pre>{{ analysisResult }}</pre>
          </el-scrollbar>
        </el-card>
        <el-empty v-else description="暂无分析结果" style="margin-top:20px"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue'
import {useRouter} from 'vue-router'
import VChart from 'vue-echarts'
import {use} from 'echarts/core'
import {CanvasRenderer} from 'echarts/renderers'
import {LineChart} from 'echarts/charts'
import {GridComponent, TooltipComponent, TitleComponent, LegendComponent} from 'echarts/components'
import {ElMessage} from 'element-plus'
import http from '@/api/http.js'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, TitleComponent, LegendComponent])

const router = useRouter()

// ------------------- 用户右上角按钮 -------------------
function logout() {
  router.push('/login')
}

function changePassword() {
  ElMessage.info('修改密码功能暂未实现')
}

// ------------------- 股票仓库 -------------------
const newStockCode = ref('')
const newStockName = ref('')
const stockList = ref([
  {code: '600519', name: '贵州茅台', price: '¥1436.78', change: 0.75, history: [1436, 1440, 1438, 1445, 1450]},
  {code: '000858', name: '五粮液', price: '¥121.48', change: -0.83, history: [121.4, 121.6, 121.3, 121.9, 122.0]},
  {code: '600036', name: '招商银行', price: '¥40.41', change: -1.25, history: [40.4, 40.5, 40.6, 40.8, 41.0]},
  {code: '601318', name: '中国平安', price: '¥87.36', change: 1.05, history: [86.8, 87.0, 87.2, 87.5, 87.36]},
  {code: '601166', name: '兴业银行', price: '¥23.45', change: -0.42, history: [23.6, 23.5, 23.4, 23.5, 23.45]},
  {code: '601668', name: '中国建筑', price: '¥7.82', change: 0.21, history: [7.8, 7.81, 7.79, 7.83, 7.82]},
  {code: '601988', name: '中国银行', price: '¥2.98', change: -0.33, history: [2.95, 2.97, 2.99, 2.96, 2.98]},
  {code: '600900', name: '长江电力', price: '¥18.42', change: 0.55, history: [18.3, 18.35, 18.4, 18.45, 18.42]},
  {code: '601857', name: '中国石油', price: '¥4.62', change: -0.65, history: [4.6, 4.63, 4.64, 4.61, 4.62]},
  {code: '600276', name: '恒瑞医药', price: '¥72.15', change: 0.92, history: [71.8, 72.0, 72.1, 72.2, 72.15]}
])
const selectedStock = ref(null)
const activeMenu = ref('stock')
const searchQuery = ref('')

function addStock() {
  if (!newStockCode.value || !newStockName.value) {
    ElMessage.warning('请输入股票代码和名称')
    return
  }
  const price = (Math.random() * 500 + 10).toFixed(2)
  const change = (Math.random() * 4 - 2).toFixed(2)
  const history = Array.from({length: 5}, (_, i) => parseFloat(price) + parseFloat((Math.random() * 2 - 1).toFixed(2)))
  stockList.value.push({
    code: newStockCode.value,
    name: newStockName.value,
    price: `¥${price}`,
    change: parseFloat(change),
    history
  })
  ElMessage.success(`${newStockName.value} 添加成功`)
  newStockCode.value = ''
  newStockName.value = ''
}

function selectStock(row) {
  selectedStock.value = row
}

function handleMenuSelect(key) {
  activeMenu.value = key
}

const filteredStocks = computed(() => !searchQuery.value ? stockList.value : stockList.value.filter(s => s.code.includes(searchQuery.value) || s.name.includes(searchQuery.value)))
const chartOption = computed(() => {
  if (!selectedStock.value) return {}
  const data = selectedStock.value.history
  return {
    tooltip: {trigger: 'axis'},
    xAxis: {type: 'category', data: ['周一', '周二', '周三', '周四', '周五']},
    yAxis: {type: 'value', min: Math.min(...data) * 0.95, max: Math.max(...data) * 1.05},
    series: [{
      name: selectedStock.value.name,
      type: 'line',
      smooth: true,
      areaStyle: {color: 'rgba(64,158,255,0.2)'},
      data
    }]
  }
})
const totalMarketValue = computed(() => 10000)
const avgChange = computed(() => {
  const total = stockList.value.reduce((sum, s) => sum + s.change, 0)
  return (total / stockList.value.length).toFixed(2)
})

function tableRowClass({row}) {
  return row === selectedStock.value ? 'current-row' : ''
}

// ------------------- PDF AI 分析 -------------------
const fileList = ref([])
const uploadedPdfs = ['茅台-2025Q3分析.pdf', '招商银行-财报分析.pdf', '五粮液-增长模型.pdf']
const selectedPdf = ref(null)
const selectedModel = ref('Hithink')
const hithinkType = ref(false)
const deepseekType = ref(false)
const analysisResult = ref('')
const loading = ref(false)

function handleUploadChange(file, files) {
  ElMessage.success(`上传成功：${file.name}（模拟）`)
  fileList.value = files
}

function downloadPdf() {
  if (!selectedPdf.value) {
    ElMessage.warning('请选择 PDF');
    return
  }
  ElMessage.success(`开始下载 ${selectedPdf.value}（模拟）`)
}

async function fetchAnalysis(model) {
  if (!selectedPdf.value) return
  selectedModel.value = model
  analysisResult.value = '分析中，请稍候...'
  loading.value = true
  try {
    const type = model === 'Hithink' ? hithinkType.value : deepseekType.value
    let res
    if (model === 'Hithink') {
      res = await http.post('/hithink/financialAssistant', {
        file_path: selectedPdf.value,
        question: '',
        type: type ? 'synopsis' : 'summary'
      }, {headers: {'Content-Type': 'application/json'}, timeout: 300000})
      analysisResult.value = res.data.reply || '（无返回内容）'
    } else {
      const url = type ? '/deepseek/synopsis' : '/deepseek/analysis'
      res = await http.post(url, {file_path: selectedPdf.value}, {
        headers: {'Content-Type': 'application/json'},
        timeout: 600000
      })
      analysisResult.value = type ? Object.entries(res.data).map(([k, v]) => `${k}：${v}`).join('\n') : res.data.reply
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
.dashboard-container {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 260px;
  background: #2c3e50;
  color: #fff;
  padding: 20px;
}

.company-info {
  text-align: center;
  margin-bottom: 20px;
}

.company-logo {
  width: 80px;
  height: 80px;
  border-radius: 50%
}

.company-name {
  margin-top: 10px;
  font-weight: bold;
  font-size: 16px
}

.menu {
  background: transparent;
  border-right: none;
}

.content {
  flex: 1;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa, #eaf0f6);
  overflow-y: auto
}

.overview-row {
  margin-bottom: 20px
}

.overview-card {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(145deg, #ffffff, #f0f4ff);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15)
}

.search-box {
  margin-bottom: 20px
}

.stock-detail-card {
  margin-top: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  padding: 20px
}

.stock-info span {
  display: inline-block;
  margin-right: 20px;
  font-size: 14px;
  color: #606266
}

.chart-container {
  margin-top: 20px
}

.current-row {
  background: #f0f4ff !important
}

.model-row {
  margin-top: 20px;
  margin-bottom: 20px
}

.model-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 20px;
  transition: all .3s
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15)
}

.model-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center
}

.result-card {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  margin-top: 20px
}

pre {
  white-space: pre-wrap;
  word-break: break-word
}

/* 右上角按钮 */
.top-right-btns {
  position: absolute;
  right: 30px;
  top: 20px;
  display: flex;
  gap: 10px;
  z-index: 10
}
</style>
