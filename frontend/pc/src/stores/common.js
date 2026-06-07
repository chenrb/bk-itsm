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

import { defineStore } from 'pinia'
import ajax from '@/utils/ajax'

export const useCommonStore = defineStore('common', {
  state: () => ({
    footer: '',
    // 检测弹窗窗体变化定时器
    slideTimeout: '',
    slideStatus: true,
    // 配置字段
    configurInfo: {},
    // 获取发现途径/工单类型/单据状态... 等公共信息
    wayInfo: {},
    // 缓存Table页面数据
    cacheTable: {},
    // 权限结构树
    permissionMeta: {
      actions: [],
      system: [],
      resources: [],
    },
    // 系统不关联资源已有权限
    systemPermission: [],
  }),
  actions: {
    // 展开 收缩
    changeWidth(value) {
      this.slideStatus = value
    },
    // 赋值配置字段
    changeConfigur(value) {
      this.configurInfo = value
    },
    // 获取发现途径/工单类型/单据状态... 等公共信息
    getWayInfo(value) {
      this.wayInfo = value
    },
    // 缓存数据
    changeCacheList(value) {
      this.cacheTable[value.type] = value.listParams
    },
    clearCacheTable() {
      this.cacheTable = {}
    },
    setPermissionMeta(data) {
      this.permissionMeta = data
    },
    setSystemPermission(data) {
      this.systemPermission = data
    },
    // 设置页面 footer
    setPageFooter(value) {
      this.footer = value
    },
    // 获取发送途径接口
    getTheWay() {
      return ajax.get(`ticket/receipts/get_global_choices/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取节点配置信息
    getConfigurInfo() {
      return ajax.get(`workflow/templates/get_global_choices/`).then((response) => {
        const res = response.data
        return res
      })
    },
    getManagePermission() {
      // IAM 接口已移除，返回空权限
      return Promise.resolve({ data: {} })
    },
    getPermissionMeta() {
      // IAM 接口已移除，使用默认空结构
      return Promise.resolve({ data: this.permissionMeta })
    },
    getIamUrl(data) {
      // IAM 接口已移除
      return Promise.resolve({ result: false, data: {} })
    },
    // 获取组织机构人员数量
    getOrganizationNumber(id) {
      return ajax.post(`gateway/usermanage/get_department_users_count/?id=${id}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取页面 footer
    getPageFooter() {
      return ajax
        .get(`footer/`, {
          baseURL: `${window.SITE_URL}core/`,
        })
        .then((response) => {
          const res = response.data
          return res
        })
    },
  },
})
