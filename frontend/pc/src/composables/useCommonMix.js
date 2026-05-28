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

import { computed } from 'vue';
import { useStore } from 'vuex';
import { useI18n } from 'vue-i18n';

/**
 * Common mix composable.
 *
 * Provides validation rules, field formatting utilities, data transformation helpers,
 * and status comparison logic.
 *
 * Uses Vuex store and vue-i18n internally.
 */
export function useCommonMix() {
  const store = useStore();
  const { t } = useI18n();

  const commonRules = computed(() => ({
    key: [
      {
        required: true,
        message: t('m.systemConfig["编码格式为英文数字及下划线"]'),
        trigger: 'blur',
      },
      {
        regex: /^[a-zA-Z0-9_]+$/,
        message: t('m.systemConfig["编码格式为英文数字及下划线"]'),
        trigger: 'blur',
      },
    ],
    name: [
      {
        required: true,
        message: t('m.systemConfig["格式为长度小于120"]'),
        trigger: 'blur',
      },
      {
        max: 120,
        message: t('m.systemConfig["格式为长度小于120"]'),
        trigger: 'blur',
      },
    ],
    smallName: [
      {
        required: true,
        message: t('m.systemConfig["格式为长度不超过8个字符"]'),
        trigger: 'blur',
      },
      {
        max: 8,
        message: t('m.systemConfig["格式为长度不超过8个字符"]'),
        trigger: 'blur',
      },
    ],
    select: [
      {
        required: true,
        message: t('m.treeinfo["字段必填"]'),
        trigger: 'blur',
      },
    ],
    color: [
      {
        regex: /^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$/,
        message: t('m.slaContent["请输入3位或6位合法色值"]'),
        trigger: 'blur',
      },
    ],
    multipleSelect: [
      {
        validator(val) {
          return val.length >= 1;
        },
        message: t('m.treeinfo["字段必填"]'),
        trigger: 'blur',
      },
    ],
    required: [
      {
        validator(val) {
          if (Array.isArray(val)) {
            return val.length >= 1;
          }
          return !!val;
        },
        message: t('m.treeinfo["字段必填"]'),
        trigger: 'input',
      },
    ],
  }));

  const keyList = {
    name: ['name', 'dayName'],
    key: ['key'],
    select: ['select', 'dayTime', 'schedule', 'handle_time', 'value'],
    color: ['color'],
    multipleSelect: ['multipleSelect'],
    required: ['required'],
  };

  const globalChoise = computed(() => {
    return store.state.common.configurInfo;
  });

  /**
   * Field cross-validation logic.
   * @param {Array} list - Fields to validate
   * @param {Array} allList - All available fields
   * @returns {Object} { validList, result }
   */
  function relatedRegex(list, allList) {
    const allRelateList = [];
    for (let i = 0; i < list.length; i++) {
      if (list[i].showFeild && list[i].regex === 'ASSOCIATED_FIELD_VALIDATION' && list[i].regex_config.rule && list[i].regex_config.rule.expressions && list[i].regex_config.rule.expressions.length) {
        const linkRule = list[i].regex_config.rule.type;
        const relateResult = {
          validList: [],
          result: '',
        };
        for (let j = 0; j < list[i].regex_config.rule.expressions.length; j++) {
          if (list[i].regex_config.rule.expressions[j].source === 'system') {
            if (list[i].regex_config.rule.expressions[j].key === 'system_time') {
              const val1 = new Date(list[i].val).getTime();
              const val2 = new Date().getTime();
              const result = checkExpressionResult(
                { name: list[i].name, val: val1, key: list[i].key },
                { name: t('m.common["系统时间"]'), val: val2 },
                list[i].regex_config.rule.expressions[j].condition,
                list[i].type
              );
              relateResult.validList.push(result);
              break;
            }
          }
          for (let k = 0; k < allList.length; k++) {
            if (list[i].regex_config.rule.expressions[j].key === allList[k].key && allList[k].showFeild) {
              const val1 = list[i].type === 'INT' ? list[i].val : new Date(list[i].val).getTime();
              const val2 = allList[k].type === 'INT' ? allList[k].val : new Date(allList[k].val).getTime();
              const result = checkExpressionResult(
                { name: list[i].name, val: val1, key: list[i].key },
                { name: allList[k].name, val: val2 },
                list[i].regex_config.rule.expressions[j].condition,
                list[i].type
              );
              relateResult.validList.push(result);
              break;
            }
          }
        }
        relateResult.result = linkRule === 'and' ? relateResult.validList.every(val => val.valid) : (!relateResult.validList.length || relateResult.validList.some(val => val.valid));
        allRelateList.push(relateResult);
      }
    }
    return {
      validList: allRelateList,
      result: allRelateList.every(val => val.result),
    };
  }

  /**
   * Check if comparison between two values meets the condition.
   */
  function checkExpressionResult(left, right, condition, type) {
    let result = {};
    const val1 = left.val;
    const val2 = right.val;
    const name1 = left.name;
    const name2 = right.name;
    switch (condition) {
      case '>':
        result = {
          valid: val1 > val2,
          tips: `"${name1}"${type === 'INT' ? t('m.newCommon["应大于"]') : t('m.newCommon["应晚于"]')}"${name2}"`,
        };
        break;
      case '<':
        result = {
          valid: val1 < val2,
          tips: `"${name1}"${type === 'INT' ? t('m.newCommon["应小于"]') : t('m.newCommon["应早于"]')}"${name2}"`,
        };
        break;
      case '==':
        result = {
          valid: val2 === val1,
          tips: `"${name1}"${t('m.newCommon["应等于"]')}"${name2}"`,
        };
        break;
      case '<=':
        result = {
          valid: val1 <= val2,
          tips: `"${name1}"${type === 'INT' ? t('m.newCommon["应不大于"]') : t('m.newCommon["应不晚于"]')}"${name2}"`,
        };
        break;
      case '>=':
        result = {
          valid: val1 >= val2,
          tips: `"${name1}"${type === 'INT' ? t('m.newCommon["应不小于"]') : t('m.newCommon["应不早于"]')}"${name2}"`,
        };
        break;
      default:
        break;
    }
    result.key = left.key;
    return result;
  }

  function standardTime(value) {
    if (!value) {
      return '';
    }
    const d = new Date(value);
    const hours = addZero(d.getHours());
    const minutes = addZero(d.getMinutes());
    const seconds = addZero(d.getSeconds());
    const gteTime = `${d.getFullYear()}-${addZero((d.getMonth() + 1))}-${addZero(d.getDate())} ${hours}:${minutes}:${seconds}`;
    return gteTime;
  }

  function standardDayTime(value) {
    if (!value) {
      return '';
    }
    const d = new Date(value);
    const gteTime = `${d.getFullYear()}-${addZero((d.getMonth() + 1))}-${addZero(d.getDate())}`;
    return gteTime;
  }

  function addZero(value) {
    const backValue = value >= 10 ? value : (`0${value}`);
    return backValue;
  }

  function checkCommonRules(value) {
    const rule = {};
    if (keyList.name.some(item => value === item)) {
      rule[value] = commonRules.value.name;
    } else if (keyList.key.some(item => value === item)) {
      rule[value] = commonRules.value.key;
    } else if (keyList.select.some(item => value === item)) {
      rule[value] = commonRules.value.select;
    } else if (keyList.color.some(item => value === item)) {
      rule[value] = commonRules.value.color;
    } else if (keyList.multipleSelect.some(item => value === item)) {
      rule[value] = commonRules.value.multipleSelect;
    } else if (keyList.required.some(item => value === item)) {
      rule[value] = commonRules.value.required;
    }
    return rule;
  }

  function typeTransition(type) {
    if (globalChoise.value.field_type) {
      const typeValue = globalChoise.value.field_type.filter(item => item.typeName === type);
      return typeValue.length ? typeValue[0].name : '';
    }
  }

  function valueTransition(itemData) {
    if (globalChoise.value.field_type) {
      let contentValue = '';
      if (itemData.type === 'FILE') {
        const tempNameList = [];
        for (const key in itemData.choice) {
          tempNameList.push(itemData.choice[key].name);
        }
        contentValue = tempNameList.join(',');
      } else {
        contentValue = itemData.choice.map(node => node.name).join(',');
      }
      return contentValue;
    }
  }

  function formattingData(node) {
    let returnValue = '';
    if (Array.isArray(node.value)) {
      returnValue = node.value.join(',');
    } else {
      if (node.type === 'INT') {
        returnValue = node.value === '' ? '' : Number(node.value);
      } else if (node.type === 'BOOLEAN') {
        returnValue = !!Number(node.value);
      } else if (node.type === 'DATETIME') {
        returnValue = standardTime(node.value);
      } else if (node.type === 'DATE') {
        returnValue = standardDayTime(node.value);
      } else {
        returnValue = node.value;
      }
    }
    return returnValue;
  }

  function fieldFormatting(valueList) {
    for (const item of valueList) {
      if (!item.showFeild) {
        continue;
      }
      item.value = item.val;
      if (item.type === 'DATETIME' || item.type === 'DATE') {
        item.value = formattingData(item);
      }
      if (item.type !== 'CUSTOMTABLE' && item.type !== 'TABLE') {
        item.value = formattingData(item);
      }
      if (item.type === 'CUSTOMTABLE') {
        const dateList = [];
        const datetimeList = [];
        item.meta.columns.forEach((meta) => {
          if (meta.display === 'date') {
            dateList.push(meta.key);
          }
          if (meta.display === 'datetime') {
            datetimeList.push(meta.key);
          }
        });
        Array.isArray(item.value) && item.value.forEach((itemValue) => {
          for (const key in itemValue) {
            if (dateList.some(meta => meta === key)) {
              itemValue[key] = standardDayTime(itemValue[key]);
            }
            if (datetimeList.some(meta => meta === key)) {
              itemValue[key] = standardTime(itemValue[key]);
            }
          }
        });
      }
    }
  }

  /**
   * Compare two nodes to see if they are the same status node.
   */
  function isSameStatusNode(nodeA, nodeB) {
    return nodeA && nodeB
      && nodeA.status === nodeB.status
      && nodeA.state_id === nodeB.state_id
      && nodeA.fields.length === nodeB.fields.length
      && nodeA.operations.length === nodeB.operations.length
      && nodeA.can_operate === nodeB.can_operate
      && nodeA.is_schedule_ready === nodeB.is_schedule_ready;
  }

  return {
    commonRules,
    keyList,
    globalChoise,
    relatedRegex,
    checkExpressionResult,
    standardTime,
    standardDayTime,
    addZero,
    checkCommonRules,
    typeTransition,
    valueTransition,
    formattingData,
    fieldFormatting,
    isSameStatusNode,
  };
}
