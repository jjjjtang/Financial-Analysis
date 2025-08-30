// src/api/http.js
import axios from 'axios'
import { API_BASE_URL } from './config.js'

// 创建 axios 实例
const http = axios.create({
    baseURL: API_BASE_URL,
    timeout: 5000,
})

export default http