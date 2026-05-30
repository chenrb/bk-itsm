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

export const useDesignStore = defineStore('design', {
  state: () => ({
    // 流程信息
    processInfo: {},
    requestStatus: false,
    show: '567',
    // 配置字段
    configurInfo: {},
    // 初始配置界面
    startConf: {
      state: false,
      info: {},
    },
    // 存储流程图数据
    flowChart: [],
    slideStatus: true,
  }),
  actions: {
    // 改变流程信息
    changeInfo(value) {
      this.processInfo = value
    },
    // 检测进入页面是否需要请求数据
    changeRequest() {
      this.requestStatus = !this.requestStatus
    },
    requestInfo(value) {
      this.processInfo.request = value
    },
    // 改变流程ID
    changeId(id) {
      this.processInfo.id = id
    },
    // 是否和业务关联
    changeBiz(bizNeed) {
      this.processInfo.is_biz_needed = bizNeed
    },
    // 赋值配置字段
    changeConfigur(value) {
      this.configurInfo = value
    },
    // 初始配置界面
    changeStartCon(value) {
      this.startConf.state = !this.startConf.state
      this.startConf.info = value
    },
    // 流程图数据
    getChart(value) {
      this.flowChart = value
    },
    // 展开 收缩
    changeWidth(value) {
      this.slideStatus = value
    },
    // 测试方法
    change(value) {
      this.show = value
    },
    // http://dev.paasbk.digitalgd.com.cn:8000/api/ticket/followers_logs/?ticket_id=103
    getfllowLog(params) {
      return ajax.get(`ticket/followers_logs/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 发送邮件提醒信息
    postFollowlogs({ params }) {
      return ajax.post(`ticket/followers_logs/notify/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取流程设计表
    getList({ params }) {
      return ajax.get(`workflow/templates/?${params}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取流程的线条和节点
    getStates(params) {
      return ajax.get(`workflow/states/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    getChartLink(params) {
      return ajax.get(`workflow/transitions/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新流程状态
    deployFlow({ params, id }) {
      return ajax.post(`workflow/templates/${id}/deploy/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除流程设计表数据
    deleteDesign({ params }) {
      return ajax.delete(`workflow/templates/${params}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新流程状态
    changeDesign({ params, id }) {
      return ajax.put(`workflow/templates/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 流程步骤一
    // 获取变更服务
    getService({ params }) {
      return ajax.get(`service/public/service_category/records/?${params}`).then((response) => {
        const res = response.data
        return res
      })
    },
    getEventType({ params }) {
      return ajax.get(`service/event/event_type/records/?${params}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取变更类型
    getChangeType() {
      return ajax.get(`service/change/change_type/records/`).then((response) => {
        const res = response.data
        return res
      })
    },
    getChangePlat() {
      return ajax.get(`service/event/plat_type/records/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 创建流程
    createFlow({ params }) {
      return ajax.post(`workflow/templates/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 流程步骤二
    // 获取图标起止点
    getStart({ id }) {
      return ajax.get(`workflow/templates/${id}/master/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新节点的位置
    updateTransitionAxis({ params, id }) {
      return ajax.patch(`workflow/transitions/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除节点
    deleteNodeInfo({ params, id }) {
      return ajax.delete(`workflow/states/${id}/`, { data: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 保存流程图
    submitChart({ params, id }) {
      return ajax.post(`workflow/templates/${id}/create_accept_transitions/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 配置页面
    // 获取某个节点信息
    getNodeInfo({ id }) {
      return ajax.get(`workflow/states/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 节点配置信息
    getConfigurInfo() {
      return ajax.get(`workflow/templates/get_global_choices/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 操作角色
    getUser({ params }) {
      return ajax.get(`role/types/?${params}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 角色关联
    getSecondUser(params) {
      return ajax.get(`role/users/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 字段列表
    getFieldList(params) {
      return ajax.get(`workflow/fields/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 新增字段
    addNewField({ params }) {
      return ajax.post(`workflow/fields/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 修改字段
    changeNewField({ params, id }) {
      return ajax.put(`workflow/fields/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 修改字段
    changeNewModuleField({ params, id }) {
      return ajax.post(`workflow/fields/${id}/update_layout/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除字段
    deleteField({ id }) {
      return ajax.delete(`workflow/fields/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 测试推送
    testInfo({ params }) {
      return ajax.get(`${params}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 上传文件
    fileUpload({ data }) {
      return ajax.post(`misc/upload_file/`, data).then((response) => {
        const res = response.data
        return res
      })
    },
    // 上传流程文件
    flowFileUpload({ fileType, data }) {
      return ajax.post(`workflow/templates/0/imports/?file_type=${fileType}`, data).then((response) => {
        const res = response.data
        return res
      })
    },
    // 字段正则规则校验
    regexList(params) {
      return ajax.get(`workflow/templates/get_regex_choice/?type=${params}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 保存配置节点
    creatNode({ params }) {
      return ajax.post(`workflow/states/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新配置
    updateNode({ params, id }) {
      return ajax.put(`workflow/states/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 流程步骤三
    // 局部更新内容
    changePartInfo({ params, id }) {
      return ajax.put(`workflow/templates/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取第一层组织架构内容
    getTreeInfo() {
      return ajax.get(`gateway/usermanage/get_first_level_departments/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取组织架构内容
    getTreeInfoChildren(params) {
      return ajax.get(`gateway/usermanage/get_department_info/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 测试
    changeValue({ value }) {
      this.show = value
    },
    putWebHook({ params, stateId }) {
      return ajax.put(`workflow/states/${stateId}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    putDevopsInfo({ params, stateId }) {
      return ajax.put(`workflow/states/${stateId}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 上传流程文件
    getComeInList(params) {
      return ajax.post(`postman/rpc_api/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
  },
})
