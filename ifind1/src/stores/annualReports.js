// src/stores/annualReports.js
import { defineStore } from 'pinia'
import http from '@/api/http'

export const useAnnualReportsStore = defineStore('annualReports', {
    state: () => ({
        reports: []
    }),
    actions: {
        async fetchReports() {
            try {
                const res = await http.get('/annualReports/getAll')
                this.reports = res.data
            } catch (err) {
                console.error('获取年报数据失败:', err)
            }
        }
    }
})