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

export const useDeployCommonStore = defineStore('deployCommon', {
  state: () => ({
    // 轮询变量
    intervalInfo: {
      basic: '',
      lines: '',
      timeOut: '',
    },
    nodeList: [],
  }),
  actions: {
    setNodeList(value) {
      this.nodeList = value || []
    },
    // 获取线条流转颜色
    getLineStatus({ basicId }) {
      return ajax.get(`ticket/receipts/${basicId}/transitions/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取节点状态列表
    getNodeList(params) {
      return ajax.get(`ticket/receipts/${params.id}/states/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 仅在单据内获取单据节点状态列表
    getOnlyTicketNodeInfo(params) {
      return ajax.get(`ticket/receipts/${params.id}/details_states/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 仅在单据内获取单据节点状态列表
    getOnlyStateStatus({ params, id }) {
      return ajax.get(`ticket/receipts/${id}/states_status/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取节点字段列表
    getTicketNodeInfo({ params, id }) {
      return ajax.get(`ticket/receipts/${id}/states/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 终止单据
    terminableOrder({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/terminate/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 转处理人
    proceedOrder({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/proceed/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    widthdrawOrder({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/withdraw/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 分派单据
    distributeOrder({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/operate/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    newAssignDeliver({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/operate/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 异常分派
    exceptionDistribute({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/exception_distribute/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 响应
    replyAssignDeliver({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/reply/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取所有关联单据
    getAssociatedTickets(params) {
      return ajax.get(`ticket/receipts/${params.id}/derive_tickets/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 关单
    closeTickets({ id, params }) {
      return ajax.post(`ticket/receipts/${id}/close/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 挂起单据
    suspendTickets({ id, params }) {
      return ajax.post(`ticket/receipts/${id}/suspend/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 恢复单据
    restoreTickets(id) {
      return ajax.post(`ticket/receipts/${id}/unsuspend/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取结束状态
    getEndStatus({ type, key }) {
      return ajax.get(`ticket_status/status/next_over_status/?service_type=${type}&key=${key}`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 执行自定义按钮
    executeCusButton({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/trigger_state_button/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 关注&取关
    setAttention({ params, id }) {
      return ajax.post(`ticket/receipts/${id}/add_follower/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 节点重试
    retryNode({ params, ticketId }) {
      return ajax.post(`/ticket/receipts/${ticketId}/retry/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 节点忽略
    ignoreNode({ params, ticketId }) {
      return ajax.post(`/ticket/receipts/${ticketId}/ignore/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 节点日志(执行信息)
    getNodeLog({ params }) {
      return ajax.get(`ticket/logs/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 通过通知url进入，获取节点是否已处理信息
    getTicketNoticeInfo({ params }) {
      return ajax.get(`ticket/receipts/operate_check/`, { params }).then((response) => {
        let res = response.data
        return res
      })
    },
  },
})
