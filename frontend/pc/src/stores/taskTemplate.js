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

export const useTaskTemplateStore = defineStore('taskTemplate', {
  state: () => ({}),
  actions: {
    // 获取任务列表
    getTemplateList(params) {
      return ajax.get(`workflow/task_schemas/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 查询单个任务信息
    getTemplateDetail(id) {
      return ajax.get(`workflow/task_schemas/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 克隆任务模板
    cloneTemplate(id) {
      return ajax.post(`workflow/task_schemas/${id}/clone/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除任务
    deleteTemplate(id) {
      return ajax.delete(`workflow/task_schemas/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 创建单个任务
    createNewTemplate(params) {
      return ajax.post(`workflow/task_schemas/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新单个任务
    updateTemplate({ params, id }) {
      return ajax.put(`workflow/task_schemas/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 创建任务字段
    createTemplateField({ params }) {
      return ajax.post(`workflow/task_field_schemas/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新任务字段
    updateTemplateField({ params, id }) {
      return ajax.patch(`workflow/task_field_schemas/${id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除模板字段
    deleteTemplateField({ id }) {
      return ajax.delete(`workflow/task_field_schemas/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取模板字段列表
    getTemplateFields(params) {
      return ajax.get(`workflow/task_field_schemas/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 引用公共触发器
    patchCloneTriggers(params) {
      return ajax.post(`trigger/triggers/clone/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除触发器
    deleteTrigger(id) {
      return ajax.delete(`trigger/triggers/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取触发器列表
    getTemplateTriggers(params) {
      return ajax.get(`trigger/triggers/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取当前stage及之前stage的字段
    getFrontFieldsList(params) {
      return ajax.get(`workflow/task_schemas/${params.id}/variables/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
  },
})
