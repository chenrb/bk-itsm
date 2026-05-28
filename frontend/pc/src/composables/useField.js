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

import { useStore } from 'vuex';
import { errorHandler } from '@/utils/errorHandler';

/**
 * Field composable.
 *
 * Provides field option fetching, value validation, and conditional field display logic.
 *
 * Uses Vuex store internally.
 */
export function useField() {
  const store = useStore();

  /**
   * Get field options based on source type (CUSTOM, API, DATADICT, RPC).
   * @param {Object} item - Field item data
   * @returns {Promise<Array>} Options array
   */
  async function getFieldOptions(item) {
    let data = [];
    switch (item.source_type) {
      case 'CUSTOM':
        data = item.choice;
        break;
      case 'API':
        data = [];
        item.choice.forEach((node) => {
          data.push({
            key: String(node.id || node.key),
            name: node.name,
            can_delete: Boolean(node.can_delete),
          });
        });
        break;
      case 'DATADICT':
        data = [];
        if (item.choice.some(it => it.can_delete)) {
          data = item.choice;
          break;
        }
        if (item.type !== 'TREESELECT') {
          await store.dispatch('datadict/get_data_by_key', {
            key: item.source_uri,
            field_key: item.key,
            service: item.service,
            current_status: item.ticket_status,
          }).then((res) => {
            data = res.data.map((ite) => {
              const temp = {
                key: ite.key,
                name: ite.name,
              };
              if (item.key === 'current_status') {
                temp['isOver'] = ite.is_over;
              }
              return temp;
            });
          })
            .catch((res) => {
              errorHandler(res);
            });
        }
        break;
      case 'RPC':
        data = [];
        if (item.choice.some(it => it.can_delete)) {
          data = item.choice;
          break;
        }
        await store.dispatch('apiRemote/getRpcData', item).then((res) => {
          data = res.data;
        })
          .catch((res) => {
            errorHandler(res);
          });
        break;
    }
    return data;
  }

  /**
   * Check if a value exists in the list.
   * @param {String} value - Value to check
   * @param {Array} list - Options list
   * @returns {Boolean|undefined}
   */
  function judgeValue(value, list) {
    if (value) return list.some(item => value.toString().indexOf(item.key) !== -1);
  }

  /**
   * Handle conditional field display logic based on show_conditions.
   * @param {Object} item - The field that triggered the change
   * @param {Array} list - All fields list
   */
  function conditionField(item, list) {
    for (let i = 0; i < list.length; i++) {
      // eslint-disable-next-line
      if (list[i].show_type || (!list[i].hasOwnProperty('show_conditions') && (!list[i].hasOwnProperty('show_result') || list[i].show_result))) {
        list[i].showFeild = true;
        continue;
      }
      if (list[i].show_conditions.expressions && list[i].show_conditions.expressions.length) {
        for (let j = 0; j < list[i].show_conditions.expressions.length; j++) {
          if (item.key === list[i].show_conditions.expressions[j].key
            && item.key === list[i].key
            && list[i].value === null) {
            list[i].showFeild = true;
          } else {
            if (item.key === list[i].show_conditions.expressions[j].key) {
              if (list[i].show_conditions.expressions.length === 1) {
                list[i].showFeild = !conditionSwitch(
                  item,
                  list[i].show_conditions.expressions[j]
                );
              } else {
                if (list[i].show_conditions.type === 'and') {
                  const statusList = [];
                  for (let z = 0; z < list[i].show_conditions.expressions.length; z++) {
                    for (let s = 0; s < list.length; s++) {
                      if (list[i].show_conditions.expressions[z].key === list[s].key) {
                        const valueStatus = conditionSwitch(
                          list[s],
                          list[i].show_conditions.expressions[z]
                        );
                        statusList.push(valueStatus);
                      }
                    }
                  }
                  list[i].showFeild = !statusList.every(status => status);
                } else {
                  const statusList = [];
                  for (let z = 0; z < list[i].show_conditions.expressions.length; z++) {
                    for (let s = 0; s < list.length; s++) {
                      if (list[i].show_conditions.expressions[z].key === list[s].key) {
                        const valueStatus = conditionSwitch(
                          list[s],
                          list[i].show_conditions.expressions[z]
                        );
                        statusList.push(valueStatus);
                      }
                    }
                  }
                  list[i].showFeild = statusList.every(status => !status);
                }
              }
            }
          }
        }
      }
    }
  }

  /**
   * Evaluate a condition between an item and a value expression.
   * @param {Object} item - Field item
   * @param {Object} value - Expression with condition and value
   * @returns {Boolean}
   */
  function conditionSwitch(item, value) {
    let statusInfo = false;
    const typeList = ['CHECKBOX', 'MEMBERS', 'MULTISELECT', 'TREESELECT'];
    const formValue = typeList.includes(item.type) ? item.val.split(',') : item.val;
    switch (value.condition) {
      case '==': {
        if (typeList.some(type => type === item.type)) {
          const valList = value.value.split(',');
          const statusList = valList.map(val => item.val.indexOf(val) === -1);
          statusInfo = ((statusList.every(status => !status)) && item.val.length === value.value.length);
        } else {
          statusInfo = (item.val === value.value || Number(item.val) === Number(value.value));
        }
        break;
      }
      case '!=': {
        if (typeList.some(type => type === item.type)) {
          const valList = value.value.split(',');
          const statusList = valList.map(val => item.val.indexOf(val) === -1);
          statusInfo = statusList.some(status => !!status)
            ? statusList.some(status => !!status) : item.val.length !== value.value.length;
        } else {
          statusInfo = (item.val !== value.value && Number(item.val) !== Number(value.value));
        }
        break;
      }
      case '>': {
        if (item.type === 'DATE' || item.type === 'DATETIME') {
          statusInfo = timeStamp(item.val) > timeStamp(value.value);
        } else {
          statusInfo = Number(item.val) > Number(value.value);
        }
        break;
      }
      case '<': {
        if (item.type === 'DATE' || item.type === 'DATETIME') {
          statusInfo = timeStamp(item.val) < timeStamp(value.value);
        } else {
          statusInfo = Number(item.val) < Number(value.value);
        }
        break;
      }
      case '>=': {
        if (item.type === 'DATE' || item.type === 'DATETIME') {
          statusInfo = timeStamp(item.val) >= timeStamp(value.value);
        } else {
          statusInfo = Number(item.val) >= Number(value.value);
        }
        break;
      }
      case '<=': {
        if (item.type === 'DATE' || item.type === 'DATETIME') {
          statusInfo = timeStamp(item.val) <= timeStamp(value.value);
        } else {
          statusInfo = Number(item.val) <= Number(value.value);
        }
        break;
      }
      case 'issuperset': {
        const issupersetList = value.value.split(',');
        statusInfo = issupersetList.every(val => formValue.includes(val));
        break;
      }
      case 'notissuperset': {
        const valnoList = value.value.split(',');
        statusInfo = valnoList.every(val => !formValue.includes(val));
        break;
      }
      default: {
        statusInfo = true;
      }
    }
    return statusInfo;
  }

  /**
   * Convert time string to timestamp.
   * @param {String} timeValue - Time string
   * @returns {Number} Timestamp
   */
  function timeStamp(timeValue) {
    const timeInfo = timeValue.replace(/-/g, '/');
    const timeStampValue = new Date(timeInfo).getTime();
    return timeStampValue;
  }

  return {
    getFieldOptions,
    judgeValue,
    conditionField,
    conditionSwitch,
    timeStamp,
  };
}
