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

import { ref, computed, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { errorHandler } from '@/utils/errorHandler';
import { deepClone } from '@/utils/util';
import i18n from '@/i18n/index.js';
import cookie from 'cookie';

const SEARCH_FORMS = [
  {
    name: i18n.t('m.tickets[\'单号/标题\']'),
    desc: i18n.t('m.tickets[\'单号/标题\']'),
    type: 'input',
    key: 'keyword',
    display: true,
    value: '',
    list: [],
    placeholder: i18n.t('m.tickets["请选择单号/标题"]'),
  },
  {
    name: i18n.t('m["项目"]'),
    desc: i18n.t('m["项目"]'),
    type: 'select',
    key: 'project_key',
    display: true,
    value: '',
    list: [],
    placeholder: i18n.t('m["请选择项目"]'),
  },
  {
    name: i18n.t('m.tickets["服务目录"]'),
    type: 'cascade',
    key: 'catalog_id',
    multiSelect: true,
    display: true,
    value: [],
    list: [],
    placeholder: i18n.t('m.tickets["请选择服务目录"]'),
  },
  {
    name: i18n.t('m.tickets["服务"]'),
    type: 'select',
    key: 'service_id__in',
    multiSelect: true,
    display: false,
    value: [],
    list: [],
    placeholder: i18n.t('m.tickets["请选择服务"]'),
  },
  {
    name: i18n.t('m.tickets["提单人"]'),
    type: 'member',
    key: 'creator__in',
    multiSelect: true,
    display: true,
    value: [],
    list: [],
    placeholder: i18n.t('m.tickets["请选择提单人"]'),
  },
  {
    name: i18n.t('m.tickets["处理人"]'),
    type: 'member',
    key: 'current_processor',
    multiSelect: true,
    display: true,
    value: [],
    list: [],
    placeholder: i18n.t('m.tickets["请选择处理人"]'),
  },
  {
    name: i18n.t('m.tickets["状态"]'),
    type: 'select',
    key: 'current_status__in',
    multiSelect: true,
    display: true,
    value: [],
    list: [],
    placeholder: i18n.t('m.tickets["请选择状态"]'),
  },
  {
    name: i18n.t('m.tickets["提单时间"]'),
    key: 'date_update',
    type: 'datetime',
    display: true,
    value: [],
    list: [],
    placeholder: i18n.t('m.tickets["请选择提单时间"]'),
  },
  {
    name: i18n.t('m.tickets["业务"]'),
    key: 'bk_biz_id',
    type: 'select',
    display: true,
    value: '',
    list: [],
    placeholder: i18n.t('m.tickets["请选择业务"]'),
  },
];

/**
 * Ticket list mixins composable.
 *
 * Provides full ticket list page state management including search forms,
 * pagination, data loading, sorting, and settings.
 *
 * Note: The consuming component must provide:
 * - `type` (Ref<String>) - The ticket list type (e.g., 'event', 'change', 'request', 'question')
 * - `isIframe` (Ref<Boolean>|Boolean) - Whether running in iframe mode
 * - `columnList` (Ref<Array>|Array) - Available column definitions
 * - `isBatch` (Ref<Boolean>) - Batch operation flag
 *
 * The `onApprovalDialogHidden` and `onOpenApprovalDialog` methods accept
 * external refs for `isBatch`, `isApprovalDialogShow`, and `approvalInfo`
 * which the consuming component should provide.
 *
 * @param {Object} params
 * @param {Ref<String>} params.type - Ticket list type
 * @param {Boolean|Ref<Boolean>} params.isIframe - Iframe mode flag
 * @param {Array|Ref<Array>} params.columnList - Column definitions
 */
export function useTicketListMixins({ type, isIframe = false, columnList = [] }) {
  const store = useStore();
  const route = useRoute();
  const { t } = useI18n();

  const searchForms = ref(deepClone(SEARCH_FORMS));
  const ticketList = ref([]);
  const setting = ref({
    fields: [],
    selectedFields: [],
    size: 'medium',
  });
  const lastSearchParams = ref({});
  const orderKey = ref('-create_at');
  const colorHexList = ref([]);
  const pagination = ref({
    current: 1,
    count: 10,
    limit: 10,
  });
  const listLoading = ref(false);
  const approvalInfo = ref({
    showAllOption: false,
    result: true,
    approvalList: [],
  });
  const isApprovalDialogShow = ref(false);
  const listError = ref(false);
  const searchToggle = ref(false);
  const isChineseLanguage = ref(true);
  const searchResultList = ref({});
  const isBatch = ref(false);

  const openFunction = computed(() => {
    return store.state.openFunction;
  });

  const currTabSettingCache = computed(() => {
    store.commit('ticket/getTicketSettingformLocalStorage');
    return store.state.ticket.settingCache[type.value];
  });

  watch(type, (newVal, oldVal) => {
    const defaultType = ['event', 'change', 'request', 'question'];
    if (newVal !== oldVal && defaultType.includes(newVal)) {
      getTypeStatus();
    }
  });

  onMounted(() => {
    getTypeStatus();
    initData();
  });

  function initData() {
    const projectKey = route.query.project_id || route.query.project_key;
    isChineseLanguage.value = cookie.parse(document.cookie).blueking_language === 'zh-cn';
    let defaultFields = ['id', 'title', 'current_steps', 'current_processors', 'create_at', 'creator', 'operate', 'status'];
    if (currTabSettingCache.value) {
      const { fields, size } = currTabSettingCache.value;
      defaultFields = fields;
      setting.value.size = size;
    }
    const columnListVal = Array.isArray(columnList) ? columnList : columnList.value;
    setting.value.fields = columnListVal.slice(0);
    setting.value.selectedFields = columnListVal.slice(0).filter(m => defaultFields.includes(m.id));
    if (projectKey) searchForms.value[1].value = projectKey || '';
    getTicketList();
    getTicketStatusTypes();
  }

  function getTicketStatusTypes() {
    const params = {
      source_uri: 'ticket_status',
    };
    store.dispatch('ticketStatus/getOverallTicketStatuses', params).then((res) => {
      searchForms.value.find(item => item.key === 'current_status__in').list = res.data;
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  function getServiceData(val) {
    const params = {
      catalog_id: val,
      is_valid: 1,
    };
    store.dispatch('catalogService/getServices', params).then((res) => {
      const formItem = searchForms.value.find(item => item.key === 'service_id__in');
      formItem.list = [];
      res.data.forEach((item) => {
        formItem.list.push({
          key: item.id,
          name: item.name,
        });
      });
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  function getTicketList() {
    const query = route.query;
    const projectKey = query.project_id || query.project_key;
    const searchParams = JSON.stringify(lastSearchParams.value) === '{}'
      ? { service_id__in: query.service_id || undefined, project_key: projectKey || undefined }
      : lastSearchParams.value;
    listLoading.value = true;
    listError.value = false;
    const isIframeVal = typeof isIframe === 'object' ? isIframe.value : isIframe;
    if (isIframeVal && Object.keys(query).length !== 0) {
      Object.keys(query).forEach(item => {
        if (item === 'project_id') {
          searchParams.project_key = projectKey;
        } else if (item === 'service_id') {
          searchParams.service_id__in = query[item];
        } else {
          searchParams[item] = query[item];
        }
      });
    }
    return store.dispatch('change/getList', {
      page_size: pagination.value.limit,
      page: pagination.value.current,
      is_draft: 0,
      view_type: `my_${type.value}`,
      ordering: orderKey.value,
      ...searchParams,
    }).then((resp) => {
      if (resp.result) {
        ticketList.value = resp.data.items.map((item) => {
          const attention = (item.followers || []).some(name => name === window.username);
          item['hasAttention'] = attention;
          item['checkStatus'] = false;
          return item;
        });
        pagination.value.count = resp.data.count;
        asyncReplaceTicketListAttr(ticketList.value);
      }
    })
      .catch((res) => {
        listError.value = true;
        errorHandler(res);
      })
      .finally(() => {
        listLoading.value = false;
      });
  }

  function asyncReplaceTicketListAttr(originList) {
    if (originList.length === 0) {
      return;
    }
    getTicketsProcessors(originList);
    getTicketsCreator(originList);
    getTicketscanOperate(originList);
  }

  function getTicketsProcessors(originList) {
    const copyList = deepClone(originList);
    const message = i18n.t('m.manageCommon[\'加载中...\']');
    originList.forEach((ticket) => {
      ticket['current_processors'] = message;
    });
    const ids = copyList.map(ticket => ticket.id);
    store.dispatch('ticket/getTicketsProcessors', { ids: ids.toString() }).then((res) => {
      if (res.result && res.data) {
        originList.forEach((ticket, index) => {
          const replaceValue = Object.prototype.hasOwnProperty.call(res.data, ticket.id)
            ? res.data[ticket.id]
            : copyList[index].current_processors;
          ticket['current_processors'] = replaceValue;
        });
      }
    });
  }

  function getTicketsCreator(originList) {
    const copyList = deepClone(originList);
    const message = i18n.t('m.manageCommon[\'加载中...\']');
    originList.forEach((ticket) => {
      ticket['creator'] = message;
    });
    const ids = copyList.map(ticket => ticket.id);
    store.dispatch('ticket/getTicketsCreator', { ids: ids.toString() }).then((res) => {
      if (res.result && res.data) {
        originList.forEach((ticket, index) => {
          const replaceValue = Object.prototype.hasOwnProperty.call(res.data, copyList[index].creator)
            ? res.data[copyList[index].creator]
            : copyList[index].creator;
          ticket['creator'] = replaceValue;
        });
      }
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  function getTicketscanOperate(originList) {
    const copyList = deepClone(originList);
    originList.forEach((ticket) => {
      ticket['can_operate'] = false;
    });
    const ids = copyList.map(ticket => ticket.id);
    store.dispatch('ticket/getTicketscanOperate', { ids: ids.toString() }).then((res) => {
      if (res.result && res.data) {
        originList.forEach((ticket) => {
          const replaceValue = Object.prototype.hasOwnProperty.call(res.data, ticket.id)
            ? res.data[ticket.id] : false;
          ticket['can_operate'] = replaceValue;
        });
      }
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  function getRowStyle({ row }) {
    return `background-color: ${row.sla_color}`;
  }

  function getTypeStatus() {
    const params = {};
    const typeVal = '';
    store
      .dispatch('ticketStatus/getTypeStatus', { type: typeVal, params })
      .then((res) => {
        colorHexList.value = res.data;
      })
      .catch((res) => {
        errorHandler(res);
      });
  }

  function getPriorityColor(row) {
    const priorityList = ['#A4AAB3', '#FFB848', '#FF5656'];
    let priorityIndex = 1;
    if (row.meta.priority) {
      priorityIndex = row.meta.priority.key > 3 ? 3 : Number(row.meta.priority.key);
    }
    return row.priority_name === '--' ? {
      background: 'none',
      color: '#424950',
    } : { backgroundColor: priorityList[priorityIndex - 1] };
  }

  function getstatusColor(row) {
    const statusColor = colorHexList.value.filter(item => item.service_type === row.service_type
      && item.key === row.current_status);
    return statusColor.length
      ? { color: statusColor[0].color_hex, border: `1px solid ${statusColor[0].color_hex}` }
      : { color: '#3c96ff', border: '1px solid #3c96ff' };
  }

  function handleSearch(params) {
    lastSearchParams.value = params;
    searchToggle.value = true;
    pagination.value.current = 1;
    getTicketList();
  }

  function deteleSearchResult(searchType, index) {
    searchResultList.value[searchType].splice(index, 1);
  }

  function handleClearSearch() {
    searchForms.value.forEach((item) => {
      if (item.key === 'service_id__in') {
        item.display = false;
      }
    });
    searchToggle.value = false;
  }

  function handleSearchFormChange(key, val) {
    if (key === 'catalog_id') {
      const formItem = searchForms.value.find(item => item.key === 'service_id__in');
      formItem.display = val.length;
      if (val.length) {
        const serviceCatalogId = val[val.length - 1];
        formItem.value = [];
        getServiceData(serviceCatalogId);
      }
    }
  }

  function onSortChange(value) {
    const sortKetMap = {
      priority_name: 'priority_order',
      status: 'current_status_order',
      create_at: 'create_at',
    };
    let order = sortKetMap[value.prop];
    if (value.order === 'descending') {
      order = `-${order}`;
    }
    orderKey.value = order;
    getTicketList();
  }

  function handlePageChange(page) {
    pagination.value.current = page;
    getTicketList();
  }

  function handlePageLimitChange(limit) {
    pagination.value.current = 1;
    pagination.value.limit = limit;
    getTicketList();
  }

  function handleSettingChange({ fields, size }) {
    setting.value.size = size;
    setting.value.selectedFields = fields;
    const fieldIds = fields.map(m => m.id);
    store.commit('ticket/setSettingCache', {
      type: type.value,
      value: { fields: fieldIds, size },
    });
    store.commit('ticket/setTicketSettingToLocalStorage');
  }

  function onChangeAttention(row) {
    const { id } = row;
    const params = {
      attention: !row.hasAttention,
    };
    let bkMessage = '';
    store.dispatch('deployOrder/setAttention', { params, id }).then(() => {
      if (row.hasAttention) {
        row.hasAttention = false;
        bkMessage = t('m.manageCommon[\'取消关注成功\']');
      } else {
        row.hasAttention = true;
        bkMessage = t('m.manageCommon[\'添加关注成功\']');
      }
      window.$bkMessage && window.$bkMessage({
        message: bkMessage,
        theme: 'success',
        ellipsisLine: 0,
      });
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  function onOpenApprovalDialog(id, result) {
    isBatch.value = false;
    isApprovalDialogShow.value = true;
    approvalInfo.value = {
      result,
      approvalList: [{ ticket_id: id }],
    };
  }

  function onApprovalDialogHidden() {
    isApprovalDialogShow.value = false;
    approvalInfo.value = {
      result: true,
      showAllOption: false,
      approvalList: [],
    };
  }

  return {
    // State
    searchForms,
    ticketList,
    setting,
    lastSearchParams,
    orderKey,
    colorHexList,
    pagination,
    listLoading,
    approvalInfo,
    isApprovalDialogShow,
    listError,
    searchToggle,
    isChineseLanguage,
    searchResultList,
    isBatch,

    // Computed
    openFunction,
    currTabSettingCache,

    // Methods
    initData,
    getTicketStatusTypes,
    getServiceData,
    getTicketList,
    asyncReplaceTicketListAttr,
    getTicketsProcessors,
    getTicketsCreator,
    getTicketscanOperate,
    getRowStyle,
    getTypeStatus,
    getPriorityColor,
    getstatusColor,
    handleSearch,
    deteleSearchResult,
    handleClearSearch,
    handleSearchFormChange,
    onSortChange,
    handlePageChange,
    handlePageLimitChange,
    handleSettingChange,
    onChangeAttention,
    onOpenApprovalDialog,
    onApprovalDialogHidden,
  };
}
