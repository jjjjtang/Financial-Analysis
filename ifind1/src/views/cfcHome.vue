<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <header class="site-header">
      <div class="nav-bar">
        <div class="logo">
          <img src="/logo.png" />
        </div>
        <nav class="nav-menu">
          <a
              v-for="item in menuItems"
              :key="item"
              href="javascript:void(0)"
              @click="handleMenuClick(item)"
          >
            {{ item }}
          </a>
        </nav>
      </div>
    </header>

    <!-- Banner -->
    <div class="banner">
      <img src="/finical.jpg" />
      <div class="banner-text">
        <h1>公司金融顾问CFC认证</h1>
        <p>权威 · 专业 · 国际化</p>
      </div>
    </div>


    <!-- 新闻中心 -->
    <section class="section news">
      <h2>新闻中心</h2>
      <el-row :gutter="20">
        <el-col v-for="news in newsList" :key="news.id" :span="8">
          <div class="card news-card">
            <img :src="news.img" />
            <h3>{{ news.title }}</h3>
            <p class="date">{{ news.date }}</p>
            <p class="snippet">{{ news.snippet }}</p>
          </div>
        </el-col>
      </el-row>
    </section>

    <!-- 底部信息 -->
    <footer class="footer">
      <p>© 2025-2025</p>
      <p>推荐使用 Chrome 浏览器，Edge</p>
      <p>电话：123-456789 地址：浙江省台州市东方大道605号</p>
    </footer>


<!--    <div class="qr-container">-->
<!--      <div-->
<!--          v-for="(qr, index) in qrs"-->
<!--          :key="index"-->
<!--          class="qr-bar"-->
<!--          @mouseenter="activeQr = index"-->
<!--          @mouseleave="activeQr = null"-->
<!--      >-->
<!--        <div class="bar"></div>-->
<!--        <div v-if="activeQr === index" class="qr-popup">-->
<!--          <img :src="qr" alt="二维码" />-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->
 </div>
</template>

<script setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'

const router = useRouter()

const menuItems = [
  '首页', '精品课程', '新闻中心', '师资团队', '精彩回顾', '金融分析', '年报分析'
]

const handleMenuClick = (item) => {
  if (item === '金融分析' || item === '年报分析') {
    router.push('/login')
  } else {
    // 其他项可以根据需要添加跳转
    console.log(`点击了：${item}`)
  }
}

const courses = ref([
  {id: 1, title: '企业投融资筹划（基础）', img: ''},
  {id: 2, title: '企业税收筹划', img: ''},
  {id: 3, title: '企业风险管理', img: ''},
  {id: 4, title: '公司金融顾问与营销实务', img: ''},
])

const newsList = ref([
  {
    id: 1,
    title: '精准对接实体经济需求，河南省某国有银行第四期CFC培训班成功举办',
    img: '/henan.png',
    date: '2025-09-08',
    snippet: '本次培训班顺利结业，参与者普遍反馈良好...'
  },
  {
    id: 2,
    title: '工商银行福建省分行CFC培训班圆满举办',
    img: '/yinhang.png',
    date: '2025-09-06',
    snippet: '课程内容贴合实际业务，受到了广泛欢迎...'
  },
  {
    id: 3,
    title: '赋能成长——广东某城商行第二期CFC培训班成功举行',
    img: '/guangdong.png',
    date: '2025-09-05',
    snippet: '本期培训更注重实战演练，培训效果显著...'
  },
])



const qrs = [
  '/qrcodes/qr1.png',
  '/qrcodes/qr2.png',
  '/qrcodes/qr3.png',
  '/qrcodes/qr4.png',
  '/qrcodes/qr5.png',
]
const activeQr = ref(null)
</script>

<style scoped>
.home-page {
  font-family: 'Microsoft YaHei', sans-serif;
  color: #333;
}

/* 顶部导航 */
.site-header {
  background: #fff;
  border-bottom: 1px solid #eee;
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
}

.logo img {
  height: 50px;
}

.nav-menu a {
  margin: 0 15px;
  font-size: 16px;
  color: #333;
  text-decoration: none;
  cursor: pointer;
}

.nav-menu a:hover {
  color: #409EFF;
}

/* Banner */
.banner {
  position: relative;
  height: 400px;
  overflow: hidden;
}

.banner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-text {
  position: absolute;
  bottom: 40px;
  left: 60px;
  color: white;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
}

.banner-text h1 {
  font-size: 36px;
  margin: 0;
}

.banner-text p {
  font-size: 20px;
}

/* 通用 section */
.section {
  padding: 60px 30px;
}

.section h2 {
  font-size: 28px;
  text-align: center;
  margin-bottom: 40px;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
}

.card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.card h3 {
  font-size: 18px;
  padding: 10px;
}

/* 新闻卡片特有 */
.news-card .date {
  font-size: 13px;
  color: #999;
  margin: 5px 0;
}

.news-card .snippet {
  font-size: 14px;
  color: #666;
  padding: 0 10px 10px;
}

/* 师资卡片 */
.teacher-card img {
  border-radius: 50%;
  width: 150px;
  height: 150px;
  margin-top: 15px;
}

.teacher-card h3 {
  margin-top: 10px;
}

.teacher-card p {
  color: #888;
  font-size: 14px;
}

/* Footer */
.footer {
  background: #2c3e50;
  color: #ccc;
  text-align: center;
  padding: 30px 10px;
  font-size: 14px;
}

/* 右下角二维码竖块样式 */
.qr-container {
  position: fixed;
  right: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.qr-bar {
  position: relative;
}

.bar {
  width: 20px;
  height: 60px;
  background-color: #409EFF;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.3s;
}

.bar:hover {
  transform: translateY(-5px);
}

.qr-popup {
  position: absolute;
  right: 30px;
  bottom: 0;
  width: 150px;
  height: 150px;
  background: white;
  border: 1px solid #ccc;
  padding: 5px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.qr-popup img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
