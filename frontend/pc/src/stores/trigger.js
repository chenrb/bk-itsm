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
import ajax from '../../utils/ajax'

export const useTriggerStore = defineStore('trigger', {
  state: () => ({
    // 流程内引用触发器，保存流程信息
    triggerVariables: [],
  }),
  actions: {
    changeTriggerVariables(list) {
      this.triggerVariables = list
    },
    // 获取触发器列表
    getTriggerTable(params) {
      return ajax.get(`/trigger/triggers/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除一个触发器
    deleteTrigger(id) {
      return ajax.delete(`/trigger/triggers/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 根据ID获取一个触发器的详细信息
    getTriggerInfo(id) {
      return ajax.get(`/trigger/triggers/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取响应事件列表信息
    getTriggerList(params) {
      return ajax.get(`/trigger/triggers/signals/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 通过触发器ID获取触发器创建下的所以规则
    getTriggerRules(params) {
      return ajax.get(`/trigger/rules/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取响应事件列表信息
    getResponseList() {
      return ajax.get(`/trigger/components/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 通过id获取响应事件的内容
    getResponseListById(params) {
      return ajax.get(`/trigger/action_schemas/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取触发器的内容
    getTriggerContent(id) {
      return ajax.get(`/trigger/actions/${id}/fields/`).then((response) => response.data)
    },
    // 获取触发器的内容
    getTriggerParams({ params, id }) {
      return ajax.post(`/trigger/actions/${id}/params/`, params).then((response) => response.data)
    },
    executeTrigger({ params, id }) {
      return ajax.post(`/trigger/actions/${id}/run/`, params).then((response) => response.data)
    },
    // 创建一个触发器规则
    createTriggerRule(params) {
      return ajax.post(`/trigger/triggers/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    createRespond({ id, params }) {
      return ajax.post(`trigger/triggers/${id}/create_or_update_action_schemas/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 一个触发器下创建多条规则
    createTriggerCondition(params) {
      return ajax.post(`/trigger/rules/batch_create_or_update/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 新一个触发器下创建多条规则
    batchTriggerCondition({ params, id }) {
      return ajax.post(`/trigger/triggers/${id}/create_or_update_rules/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 全量修改一个触发器规则
    putTriggerRule({ params, id }) {
      return ajax.put(`/trigger/triggers/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取触发器变量
    getTriggerVariables({ id, type, params }) {
      return ajax.get(`workflow/${type}/${id}/variables/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取单据手动触发器
    getTicketHandleTriggers({ id, params }) {
      return ajax.get(`ticket/receipts/${id}/trigger_actions/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取单据触发器记录
    getTicketTriggerRecord({ id, params }) {
      return ajax.get(`ticket/receipts/${id}/trigger_actions_group/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取单据手动触发器
    executeHandleTriggers(id) {
      return ajax.post(`trigger/actions/${id}/run/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取任务手动触发器
    getTaskHandleTriggers(params) {
      return ajax.get(`trigger/actions/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
  },
})
