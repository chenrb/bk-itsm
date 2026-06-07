/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2025 Tencent.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

/**
 * 全局变量默认值
 *
 * 后端配置变量由 index.html / vite 插件注入。
 * 此处声明默认值，确保变量在任何代码访问前已定义。
 */

// 用户数据
window.username = window.username || ''
window.chname = window.chname || ''
window.IS_ITSM_ADMIN = window.IS_ITSM_ADMIN || 0
window.all_access = window.all_access || []
window.DEFAULT_PROJECT = window.DEFAULT_PROJECT || ''
window.PERMISSIONS = window.PERMISSIONS || []

// 平台配置
window.PLATFORM_NAME = window.PLATFORM_NAME || ''
window.BRAND_NAME = window.BRAND_NAME || 'ITSM'
window.FAVICON = window.FAVICON || '/static/core/images/bk_itsm.png'
window.APP_LOGO = window.APP_LOGO || '/static/core/images/bk_itsm.png'
window.FOOTER = window.FOOTER || ''
