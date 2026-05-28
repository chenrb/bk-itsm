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

import _ from 'lodash';
import { useStore } from 'vuex';
import { getCurrentInstance, watch } from 'vue';
import { errorHandler } from '@/utils/errorHandler';

/**
 * API fields watch composable.
 *
 * Handles priority fetching, data dictionary fetching, cascading API field data,
 * debounced data refreshing, and field dependency watching.
 *
 * Uses Vuex store internally.
 * Note: The `isNecessaryToWatch` method uses `getCurrentInstance()` to access
 * the component instance for `vm.$watch`. The consuming component must call this
 * within setup().
 *
 * @param {Object} [componentInstance] - Optional component instance override. If not provided, uses getCurrentInstance().
 */
export function useApiFieldsWatch(componentInstance) {
  const store = useStore();
  const instance = componentInstance || getCurrentInstance();

  /**
   * Get priority for a field based on impact and urgency.
   * @param {Object} params - Query parameters
   * @param {Object} itemRelate - The related field item
   */
  async function get_priority(params, itemRelate) {
    const data = JSON.parse(JSON.stringify(params));
    data.service_type = itemRelate.service;
    delete data.id;
    const preFieldParams = {
      id: itemRelate.ticket_id,
    };
    if (!(data.impact && data.urgency)) {
      await store.dispatch('change/getStepList', preFieldParams).then((res) => {
        res.data.forEach((node) => {
          node.fields.forEach((field) => {
            if (field.key === 'urgency') {
              data.urgency = params.urgency || field.value;
            }
            if (field.key === 'impact') {
              data.impact = params.impact || field.value;
            }
          });
        });
      }, (res) => {
        errorHandler(res);
      });
    }
    store.dispatch('apiRemote/get_priority', { data }).then((res) => {
      itemRelate.val = res.data;
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  /**
   * Get data dictionary by key.
   * @param {Object} itemRelate - Field item
   * @returns {Promise}
   */
  async function get_data_by_key(itemRelate) {
    return store.dispatch('datadict/get_data_by_key', {
      key: itemRelate.source_uri,
      field_key: itemRelate.key,
      service: itemRelate.service,
      current_status: itemRelate.related_fields
        ? itemRelate.ticket_status : itemRelate.ticket_status,
    }).then((res) => {
      itemRelate.choice = res.data.map(item => ({
        key: item.key,
        name: item.name,
      }));
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  /**
   * Get API remote data for cascading fields.
   * @param {Object} params - Request parameters
   * @param {Object} field - The field to update
   * @param {String} type - Type: 'workflow', 'submit', or default
   * @returns {Promise}
   */
  function apiRemoteGetData(params, field, type) {
    let reqParams = JSON.parse(JSON.stringify(params));
    let url = 'apiRemote/get_data';
    if (type === 'workflow') {
      url = 'apiRemote/get_data_workflow';
    }
    if (type === 'submit') {
      url = 'apiRemote/get_data_receipts';
      reqParams = {
        api_instance_id: field.api_instance_id,
        kv_relation: field.kv_relation,
        fields: reqParams,
      };
    }
    reqParams.id = field.id;
    reqParams.kv_relation = field.kv_relation;
    reqParams.api_instance_id = field.api_instance_id;
    reqParams.api_info = field.api_info;

    return store.dispatch(url, reqParams).then((res) => {
      field.choice = [];
      const choice = res.data.map(item => ({
        key: item.key || item.id,
        name: item.name,
      }));
      choice.forEach((itemRefresh) => {
        field.choice.push(JSON.parse(JSON.stringify(itemRefresh)));
      });
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  /**
   * Debounced wrapper that routes to get_priority or apiRemoteGetData.
   */
  const debounce = _.debounce(async (params, itemRelate, vm, type, refreshComp) => {
    if (itemRelate.key === 'priority') {
      vm.get_priority(params, itemRelate, type);
      return false;
    }
    vm.apiRemoteGetData(params, itemRelate, type, refreshComp);
  }, 1000, {
    leading: true,
    trailing: true,
    maxWait: 2000,
  });

  /**
   * Determine if fields need watching and set up watchers for field dependencies.
   * Must be called within setup() as it uses getCurrentInstance() for $watch.
   *
   * @param {Object} item - Node object with fields array
   * @param {String} type - Type context ('workflow', 'submit', etc.)
   * @param {Function} refreshComp - Optional callback after data loads
   */
  async function isNecessaryToWatch(item, type, refreshComp) {
    const promiseQueue = [];
    item.fields.forEach((field) => {
      if (field.type === 'DATADICT' && field.type !== 'TREESELECT') {
        promiseQueue.push(get_data_by_key(field));
      }
      if ((field.source_type === 'API' || field.key === 'priority')
        && !field.choice.some(it => it.can_delete)
      ) {
        const params = {
          id: field.id,
          api_instance_id: field.api_instance_id,
          kv_relation: field.kv_relation,
        };
        if (field.related_fields && field.related_fields.rely_on) {
          field.related_fields.rely_on.forEach((itefinal) => {
            const targetField = item.fields.find(f => f.key === itefinal);
            if (targetField) {
              params[itefinal] = targetField.val || '';
            }
          });
        }
        if (Object.values(params).every(p => !!p) && item.key !== 'priority') {
          promiseQueue.push(apiRemoteGetData(params, field, type));
        }
      }
    });
    Promise.all(promiseQueue).then(() => {
      refreshComp && refreshComp();
    });

    // Field dependency watching setup
    const CurrentApiFields = item.fields.filter(ite => (ite.source_type === 'API' || ite.key === 'priority')
      && ite.related_fields && ite.related_fields.rely_on
      && ite.related_fields.rely_on.length);
    if (!CurrentApiFields.length) {
      return;
    }
    let relyOnFieldsKeyList = [];
    CurrentApiFields.forEach((ite) => {
      relyOnFieldsKeyList = relyOnFieldsKeyList.concat(ite.related_fields.rely_on);
    });
    const CurrentreBeReliedFields = item.fields.filter(ite => ite.related_fields && ite.related_fields.be_relied
      && ite.related_fields.be_relied.length);
    if (!CurrentreBeReliedFields.length) {
      return;
    }
    const CurrentrelyOnFields = CurrentreBeReliedFields
      .filter(ite => relyOnFieldsKeyList.indexOf(ite.key) !== -1);
    if (!CurrentrelyOnFields.length) {
      return;
    }

    // Use Vue's watch API to watch the reactive field values
    // Note: This requires the consuming component to provide the instance proxy
    const vm = instance?.proxy || instance;

    CurrentrelyOnFields.forEach((ite) => {
      watch(
        () => ite.val,
        () => {
          if (ite.val) {
            const rca = CurrentApiFields
              .filter(item_ => item_.related_fields.rely_on.indexOf(ite.key) !== -1);
            rca.forEach(async (itemRelate) => {
              const relateCurrentreBeRelied = CurrentrelyOnFields
                .filter(itemRe => itemRelate.related_fields.rely_on.indexOf(itemRe.key) !== -1);
              const isALlFill = relateCurrentreBeRelied.every(itemRely => itemRely.val);
              if (isALlFill || false) {
                const params = {
                  id: itemRelate.id,
                  api_instance_id: itemRelate.api_instance_id,
                  kv_relation: itemRelate.kv_relation,
                };
                if (itemRelate.related_fields && itemRelate.related_fields.rely_on) {
                  itemRelate.related_fields.rely_on.forEach((itefinal) => {
                    const currTargetField = CurrentrelyOnFields.find(f => f.key === itefinal);
                    const targetField = item.fields.find(f => f.key === itefinal);
                    if (targetField) {
                      params[itefinal] = currTargetField.val || '';
                    }
                  });
                }
                if (itemRelate.key !== 'priority') {
                  itemRelate.choice.splice(0, itemRelate.choice.length);
                  itemRelate.val = '';
                }
                debounce(params, itemRelate, { get_priority, apiRemoteGetData }, type);
              }
            });
          }
        },
        { deep: true }
      );
    });
  }

  /**
   * Refresh data source for a field based on changed dependency fields.
   * @param {Object} item - The field to refresh
   * @param {Array} changeFields - Fields that changed
   * @param {String} type - Type context
   */
  function freshApi(item, changeFields, type) {
    const params = {};
    const keyList = changeFields.map(itemfiter => itemfiter.key);
    if (item.related_fields && item.related_fields.rely_on) {
      item.related_fields.rely_on.forEach((itefinal) => {
        const relateobj = changeFields.filter(itemFi => itemFi.key === itefinal)[0];
        if (keyList.indexOf(itefinal) !== -1) {
          params[itefinal] = relateobj ? (relateobj.val || '') : '';
        }
      });
    }
    if (Object.values(params).every(item => !!item) || false) {
      item.choice.splice(0, item.choice.length);
      item.val = '';
      debounce(params, item, { get_priority, apiRemoteGetData }, type);
    }
  }

  return {
    get_priority,
    get_data_by_key,
    apiRemoteGetData,
    debounce,
    isNecessaryToWatch,
    freshApi,
  };
}
