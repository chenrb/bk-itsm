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
import { fileDownload } from '@/utils/util'

export const useApiRemoteStore = defineStore('apiRemote', {
  state: () => ({}),
  actions: {
    test_field_api_choices(params) {
      return ajax.post(`postman/remote_api/test_field_api_choices/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    get_user_project_list() {
      return ajax.get(`gateway/sops/get_user_project_list/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取级联字段数据源 （工单）
    get_data(params) {
      return ajax.post(`ticket/fields/${params.id}/api_field_choices/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取级联字段数据源 （流程--单据预览/字段隐藏。。。）
    get_data_workflow(params) {
      return ajax.post(`postman/api_instance/${params.api_instance_id}/field_choices/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取级联字段数据源 （提单）
    get_data_receipts(params) {
      return ajax.post(`ticket/receipts/api_field_choices/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取当前项目、系统api分类
    get_all_remote_system(params) {
      return ajax.get('postman/remote_system/all/', { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取系统分类列表
    get_remote_system(params) {
      return ajax.get(`postman/remote_system/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 创建分类
    post_remote_system(params) {
      return ajax.post(`postman/remote_system/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新API
    put_remote_system(params) {
      return ajax.put(`postman/remote_system/${params.id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 删除分类
    delete_remote_system(id) {
      return ajax.delete(`postman/remote_system/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取API列表
    get_remote_api(params) {
      return ajax.get(`postman/remote_api/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 创建API
    post_remote_api(params) {
      return ajax.post(`postman/remote_api/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 更新API
    put_remote_api(params) {
      return ajax.put(`postman/remote_api/${params.id}/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取API详情
    get_remote_api_detail(params) {
      return ajax.get(`postman/remote_api/${params.id}/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    export_api(id) {
      return ajax.get(`postman/remote_api/${id}/exports/`, {
        transitional: {
          forcedJSONParsing: false,
        },
        responseType: 'blob',
      }).then((response) => {
        fileDownload(response)
      })
    },
    run_remote_api(params) {
      return ajax.post(`postman/remote_api/${params.id}/run_api/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    delete_api(id) {
      return ajax.delete(`postman/remote_api/${id}/`).then((response) => {
        const res = response.data
        return res
      })
    },
    batch_delete_apis(params) {
      return ajax.post(`postman/remote_api/batch_delete/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取code接口
    get_systems(params) {
      return ajax.get(`postman/remote_system/get_systems/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取api列表
    get_components(params) {
      return ajax.get(`postman/remote_system/get_components/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    get_related_fields(params) {
      return ajax.get(`workflow/states/${params.state}/variables/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取会签所有条件选项
    get_sign_conditions(id) {
      return ajax.get(`workflow/states/${id}/sign_variables/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取会签日志
    get_sign_logs(params) {
      return ajax.get(`ticket/logs/`, { params }).then((response) => {
        const res = response.data
        return res
      })
    },
    get_api_import({ fileType, data }) {
      return ajax.post(`postman/remote_api/0/imports/?file_type=${fileType}`, data).then((response) => {
        const res = response.data
        return res
      })
    },
    get_priority({ data }) {
      return ajax.post(`sla/matrixs/priority_value/`, data).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取RPC数据
    getRpcData(params) {
      return ajax.post(`postman/rpc_api/`, params).then((response) => {
        const res = response.data
        return res
      })
    },
  },
})
