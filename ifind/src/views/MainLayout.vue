<template>
  <div class="main-container">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div style="display: flex">
        <div class="logo">
          <img src="../../public/logo.png" style="height: 45px; width: 45px; padding-top: 7px;padding-left: 15px">
          <img src="../../public/logo.png" style="height: 45px; width: 45px; padding-top: 7px;padding-left: 15px">
        </div>
        <div style="background-color: #2C2F39; padding-top: 18px;padding-left: 17px;font-size: 20px;font-weight: bold;width: 100%">
          财报分析系统
        </div>
      </div>

      <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
      >
        <el-menu-item index="/Main/Dashboard" @click="$router.push('/Main/Dashboard')">
          <i class="el-icon-menu"></i>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/Main/FinancialSummary" @click="$router.push('/Main/FinancialReport')">
          <i class="el-icon-document-checked"></i>
          <span>财报摘要</span>
        </el-menu-item>
<!--        <el-menu-item index="/Main/MarketOverview" @click="$router.push('/Main/MarketOverview')">-->
<!--          <i class="el-icon-s-data"></i>-->
<!--          <span>市场概览</span>-->
<!--        </el-menu-item>-->
<!--        <el-menu-item index="/Main/CompanyInfo" @click="$router.push('/Main/CompanyInfo')">-->
<!--          <i class="el-icon-user"></i>-->
<!--          <span>公司信息</span>-->
<!--        </el-menu-item>-->
      </el-menu>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-content">
      <div class="navbar">
        <div class="left">当前位置：首页</div>
        <div class="right">
          <el-dropdown>
            <span class="el-dropdown-link">
              用户名<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item>个人中心</el-dropdown-item>
              <el-dropdown-item>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
      <div class="content-area">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'MainLayout',
  methods: {},
  computed: {
    activeMenu() {
      return this.$route.path
    }
  }
}
</script>

<style scoped>
.main-container
{
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar
{
  width: 220px;
  background-color: #304156;
  color: white; height: 100%;
  transition: width 0.3s;
}
.logo
{
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff; background-color: #2b2f3a; }
.el-menu-vertical
{
  border-right: none;
}
.main-content
{
  flex: 1; display: flex;
  flex-direction: column;
  overflow: hidden;
}
.navbar
{ height: 60px;
  line-height: 60px;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
.content-area
{ flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f0f2f5; }
.el-dropdown-link
{
  cursor: pointer;
  color: #409EFF;
}
</style>
