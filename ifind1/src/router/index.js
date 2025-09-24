import { createRouter, createWebHistory } from 'vue-router'

// 页面组件导入
import Login from '../components/Login.vue'
import MainLayout from '../views/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import FinancialReport from '../views/FinancialReport.vue'
import MarketOverview from '../views/MarketOverview.vue'
import CompanyInfo from '../views/CompanyInfo.vue'
import HomeView from "@/views/HomeView.vue"
import CfcHome from '../views/cfcHome.vue'

const routes = [
    {
        path: '/',
        redirect: '/cfcHome', // 默认重定向到登录页
    },
    {
        path: '/home',
        name: 'HomeView',
        component: HomeView,
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
    },
    {
        path: '/cfchome',
        name: 'CfcHome',
        component: CfcHome,
    },
    {
        path: '/Main',
        name: 'Main',
        component: MainLayout,
        meta: { requiresAuth: true },
        children: [
            {
                path: 'Dashboard',
                name: 'Dashboard',
                component: Dashboard,
            },
            {
                path: 'FinancialReport',
                name: 'FinancialReport',
                component: FinancialReport,
            },
            {
                path: 'MarketOverview',
                name: 'MarketOverview',
                component: MarketOverview,
            },
            {
                path: 'CompanyInfo',
                name: 'CompanyInfo',
                component: CompanyInfo,
            },
        ],
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') // 简化示例

    if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
        next('/login') // 拦截未登录用户
    } else {
        next() // 放行
    }
})

export default router
