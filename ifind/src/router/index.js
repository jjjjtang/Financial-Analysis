import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import MainLayout from '../views/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import FinancialReport from '../views/FinancialReport.vue'
import MarketOverview from '../views/MarketOverview.vue'
import CompanyInfo from '../views/CompanyInfo.vue'
const routes = [
    {
        path: '/',
        redirect: '/login',
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
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
                component: Dashboard
            },
            {
                path: 'FinancialReport',
                name: 'FinancialReport',
                component: FinancialReport
            },
            {
                path: 'MarketOverview',
                name: 'MarketOverview',
                component: MarketOverview
            },
            {
                path: 'CompanyInfo',
                name: 'CompanyInfo',
                component: CompanyInfo
            }
        ]
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

//添加路由守卫
// router.beforeEach((to, from, next) => {
//     const isAuthenticated = localStorage.getItem('isAuthenticated') // 简单示例，实际项目中应该使用Vuex或Pinia
//
//     if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
//         next('/login') // 如果访问需要认证的页面且未登录，则跳转到登录页
//     } else {
//         next() // 否则继续
//     }
// })

export default router