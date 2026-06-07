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
import ajax from '../utils/ajax'
import { jsonp } from '../utils/util'
import i18n from '@/i18n/index.js'

/** 设置浏览器标签页 favicon */
function setShortcutIcon(url) {
  let link = document.querySelector('link[rel="shortcut icon"]');
  if (!link) {
    link = document.createElement('link');
    link.setAttribute('rel', 'shortcut icon');
    document.head.appendChild(link);
  }
  const extMap = { ico: 'x-icon', png: 'png', svg: 'svg+xml' };
  const ext = url ? url.split('/').pop().split('?')[0].split('.')[1] : '';
  if (ext) link.setAttribute('type', `image/${extMap[ext] || ext}`);
  link.setAttribute('href', url);
}

const t = i18n.global.t.bind(i18n.global);

export const useRootStore = defineStore('root', {
  state: () => ({
    language: "zh-cn",
    showNotice: false,
    // 任务执行后刷新任务记录列表
    taskHistoryRefresh: false,
    // 缓存人员选择器数据
    memberList: [],
    // 提单成功信息
    subinfo: null,
    // 屏宽
    clientWidth: null,
    // 工作台图表数据
    drawType: {},
    drawTime: {},
    drawStatus: {},
    // 运营图表数据
    operationalall: {},
    operationalmodule: {},
    // 自定义数据
    customList: [],
    customDict: {},
    choice_type_list: [],
    serviceList: [],
    commomInfo: {
      choice_state_list_dict: {},
      export_fields: [],
    },
    // 系统当前登录用户
    user: {},
    // iFrame加载状态
    isIframeLoading: true,
    // 权限状态
    permisStatus: {},
    // 我的待办和待认领
    myToDoInfo: false,
    basicId: "",
    // file状态
    fileStatus: false,
    // 所属业务 -- 接口数据缓存
    business: [],
    faultType: [],
    openFunction: {
      SYS_FILE_PATH: false,
      FLOW_PREVIEW: false,
      CHILD_TICKET_SWITCH: false,
      WIKI_SWITCH: false,
      SLA_SWITCH: false,
      TRIGGER_SWITCH: false,
      TASK_SWITCH: false,
      TABLE_FIELDS_SWITCH: false,
      FIRST_STATE_SWITCH: false,
    },
    platformInfo: {
      favicon: window.FAVICON,
      name: window.PLATFORM_NAME,
      brandName: window.BRAND_NAME,
      version: window.VERSION,
      appLogo: window.APP_LOGO,
      i18n: {}
    },
  }),
  getters: {
    // 深复制
    deepcopy: (state) => {
      function deepcopy(item) {
        if (!item) {
          return item
        }
        if (item.constructor === Object) {
          const itemobject = {}
          const keys = Object.keys(item)
          if (keys.length) {
            keys.map((it) => {
              itemobject[it] = deepcopy(item[it])
            })
          }
          return itemobject
        } else if (item.constructor === Array) {
          const itemarray = []
          if (item.length) {
            item.map((ite) => {
              itemarray.push(deepcopy(ite))
            })
          }
          return itemarray
        } else {
          return item
        }
      }
      return deepcopy
    },
    // 数据校验isSub
    dataCheck: (state) => {
      function dataCheck(data, type) {
        // 非空校验
        if (!data) {
          return t(`m.wiki["不能为空"]`)
        }
        // 长度校验
        let typelist
        let islength
        let minlength
        let maxlength
        // type eg: 'Metacharacter_1$length^150_chinse'
        if (type) {
          typelist = type.toString().split("_")
          type = typelist[0]
          typelist.forEach((item) => {
            if (item.indexOf("length") !== -1) {
              islength = true
              if (item.indexOf("$") !== -1) {
                minlength = item.split("$")[0]
              }
              if (item.indexOf("^") !== -1) {
                maxlength = item.split("^")[1]
              }
            }
          })
          if (islength) {
            if (minlength && data.length < minlength) {
              return t("m.wiki['长度应大于']") + `${minlength}`
            }
            if (maxlength && data.length > maxlength) {
              return t("m.wiki['长度应小于']") + `${minlength}`
            }
            // 默认不超过255
            if (data.length > 255) {
              return t("m.wiki['长度1~255']")
            }
          }
        }
        // 多类型校验 /^[一-龥_a-zA-Z0-9]+$/
        switch (type) {
          case "Metacharacter":
            // 判断输入字符串是否为中文、数字、字母、下划线组成
            if (typelist && typelist.indexOf("chinse") !== -1) {
              if (/^[一-龥_a-zA-Z0-9]+$/.test(data)) {
                return ""
              }
              return t("m.wiki['内容应由中文、数字、字母、下划线组成]")
            }
            // 判断输入字符串是否为数字、字母、下划线组成
            if (/^\w+$/.test(data)) {
              return ""
            }
            return t("m.wiki['内容应由数字、字母、下划线组成]")
          case "Number":
            // 判断输入字符串是否为数字、字母、下划线组成
            if (/^\d+$/.test(data)) {
              return ""
            }
            return t("m.wiki['请填写数字']")
          default:
            return ""
        }
      }
      return dataCheck
    },
  },
  actions: {
    // 设置语言
    setLanguage(value) {
      this.language = value
    },
    setNoticeShow(value) {
      this.showNotice = value
    },
    // 人员选择数据
    changMemberList(value) {
      this.memberList = value
    },
    // 改变file的上传状态
    changeFileStatus(value) {
      this.fileStatus = value
    },
    // 所属业务缓存
    storeBusiness(value) {
      this.business = value
    },
    // 故障类型缓存
    storeFault(value) {
      this.faultType = value
    },
    setIframeLoadingState(payload) {
      this.isIframeLoading = payload.status
    },
    changeBasicId(value) {
      this.basicId = value
    },
    // 改变权限设置
    changePermis(value) {
      this.permisStatus = value
    },
    // 自定义数据
    changeCustom(value) {
      this.customList = value
    },
    // 公共数据
    getTypeWay(value) {
      this.commomInfo["export_fields"] = value["export_fields"]
      this.commomInfo["choice_state_list_dict"] = value["choice_state_list_dict"]
      this.commomInfo["processor_type"] = value["processor_type"]
    },
    // 工作台图表数据
    getdrawType(value) {
      this.drawType = value
    },
    getdrawTime(value) {
      this.drawTime = value
    },
    getdrawStatus(value) {
      this.drawStatus = value
    },
    // 运营图表数据
    setoperationalall(value) {
      this.operationalall[value[0]] = value[1]
    },
    setoperationalmodule(value) {
      this.operationalmodule[value[0]] = value[1]
    },
    // 屏宽
    changeClient(value) {
      this.clientWidth = value
    },
    // 我的待办和待认领
    changeMyData(value) {
      this.myToDoInfo = value
    },
    // 全选函数
    allselected(obj) {
      if (obj.vm[obj.dic][obj.isall]) {
        if ((obj.key.indexOf("all") !== -1) | (obj.data.length === obj.datalist.length - 1)) {
          // 全选
          obj.vm[obj.dic][obj.Selected] = obj.datalist.map((item) => {
            return item.key
          })
          obj.vm[obj.dic][obj.isall] = false
        }
      } else {
        if (obj.key.indexOf("all") !== -1) {
          // 去掉 全选--all
          obj.vm[obj.dic][obj.Selected].splice(0, 1)
        } else {
          // 取消全选
          obj.vm[obj.dic][obj.Selected] = []
        }
        obj.vm[obj.dic][obj.isall] = true
      }
    },
    changeMsg(obj) {
      this.choice_type_list = obj
    },
    taskHistoryRefreshFunc() {
      this.taskHistoryRefresh = !this.taskHistoryRefresh
    },
    changeOpenFunction(obj) {
      this.openFunction = obj
    },
    setPlatformInfo(content) {
      this.platformInfo = content
    },
    updateUserLanguage(language) {
      const bkPaasEsbHost = window.BK_PAAS_ESB_HOST
      return jsonp(bkPaasEsbHost + '/api/c/compapi/v2/usermanage/fe_update_user_language/', language)
    },
    getPlatformPreData() {
      return ajax.get('current_user/').then((response) => {
        if (!response || !response.data || !response.data.data) return
        const data = response.data.data
        window.DEFAULT_PROJECT = data.DEFAULT_PROJECT || ''
        window.IS_ITSM_ADMIN = data.IS_ITSM_ADMIN || 0
        window.all_access = data.all_access || []
        window.chname = data.chname || ''
        window.username = data.username || ''
        window.PERMISSIONS = data.permissions || []
        return data
      })
    },
    /**
     * 获取项目里面的 rtx 人员选择器数据
     *
     * @param {string} projectId 项目 id
     *
     * @return {Promise} promise 对象
     */
    getProjectRtxList({ projectId }) {
      return ajax.get(`api/projects/users/?project_id=${projectId}`).then((response) => response.data)
    },
    // 自定义列表数据
    getCustom() {
      return ajax.get(`service/categories/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 自定义列表数据 -- dict
    getCustomDict() {
      return ajax.get(`service/categories/translate_view/`).then((response) => {
        const res = response.data
        this.customDict = res.data
        return res
      })
    },
    // 权限中心
    getPermiss() {
      return ajax.get(`role/users/extra/get_access_by_user/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取首页待办
    getHomeProcess() {
      return ajax.get(`ticket/receipts/mine/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取最新动态
    getlogList() {
      return ajax.get(`ticket/logs/get_index_ticket_event_log/`).then((response) => {
        const res = response.data
        return res
      })
    },
    // 获取单个人员的详细信息
    getPersonInfo(params) {
      return ajax.get(`gateway/bk_login/get_batch_users/`, { params: params }).then((response) => {
        const res = response.data
        return res
      })
    },
    // 通过部门 id 获取部门信息
    getDepartmentInfo(params) {
      return ajax.get(`gateway/usermanage/get_department_info/`, { params: params }).then((response) => {
        let res = response.data
        return res
      })
    },
    // 获取标准运维流程模板
    getTemplateList(params) {
      return ajax.get(`gateway/sops/get_template_list/`, { params: params }).then((response) => response.data)
    },
    // 获取标准运维流程模板
    getTemplateDetail(params) {
      return ajax.get(`gateway/sops/get_template_detail/`, { params: params }).then((response) => response.data)
    },
    // 获取标准运维方案列表
    getTemplatePlanList(params) {
      return ajax.get(`gateway/sops/get_sops_template_schemes/`, { params: params }).then((response) => response.data)
    },
    // 创建标准运维任务
    createTask(params) {
      return ajax.post(`task/create_task/`, params).then((response) => response.data)
    },
    getTaskList(query) {
      return ajax.get("task/get_tasks/", { params: { ...query } }).then((response) => response.data)
    },
    operateTask(params) {
      return ajax.post(`task/operate_task/`, params).then((response) => response.data)
    },
    startTask(params) {
      return ajax.post(`task/start_task/`, params).then((response) => response.data)
    },
    /**
     * 获取当前用户的全局设置（从 init 接口已获取的数据中读取）
     * @returns {Object}
     */
    async getGlobalConfig() {
      const { i18n, name, brandName } = this.platformInfo
      document.title = `${i18n?.name || name} | ${i18n?.brandName || brandName}`
      setShortcutIcon(this.platformInfo.favicon)
      return this.platformInfo
      return resp
    },
  },
})
