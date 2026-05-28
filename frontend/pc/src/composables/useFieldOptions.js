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
import { useI18n } from 'vue-i18n';
import { errorHandler } from '@/utils/errorHandler';

/**
 * Field options composable.
 *
 * Provides methods for fetching field options from different sources (CUSTOM, API, DATADICT)
 * and handling field selection with related field dependencies.
 *
 * Note: `debounce` creates a debounced function that expects `item` and `options`
 * to be reactive refs from the consuming component. The consuming component
 * should pass these refs so the debounced function can update them.
 *
 * @param {Object} params
 * @param {Ref} params.item - Reactive ref for the current field item
 * @param {Ref} params.options - Reactive ref for the field options list
 * @param {Ref} params.fields - Reactive ref for all fields array (needed for itemSelect)
 * @param {Boolean} params.isPreview - Whether the form is in preview mode
 */
export function useFieldOptions({ item, options, fields, isPreview = false }) {
  const store = useStore();
  const { t } = useI18n();

  const debounce = _.debounce(async () => {
    item.value.choice = await getFieldOptions(item.value, isPreview);
    options.value = item.value.choice;
  }, 1000, {
    leading: true,
    trailing: true,
    maxWait: 2000,
  });

  /**
   * Get field options based on source type.
   * @param {Object} itemData - Field item data
   * @param {Boolean} type - Is preview mode
   * @returns {Promise<Array>} Options array
   */
  async function getFieldOptions(itemData, type) {
    await itemData;
    let data = [];
    switch (itemData.source_type) {
      case 'CUSTOM':
        data = itemData.choice;
        break;
      case 'API':
        if (type && itemData.id) {
          const reqParams = itemData.relyOn || {};
          reqParams.id = itemData.id;
          await store.dispatch('apiRemote/get_data', reqParams).then((res) => {
            data = res.data.map(item => ({
              key: item.key,
              name: item.name,
            }));
          })
            .catch((res) => {
              errorHandler(res);
            });
        } else {
          data = [];
          itemData.choice.forEach((node) => {
            data.push({
              key: node.id,
              name: node.name,
            });
          });
        }
        break;
      case 'DATADICT':
        if (type && itemData.type !== 'TREESELECT') {
          await store.dispatch('datadict/get_data_by_key', {
            key: itemData.source_uri,
            field_key: itemData.key,
            service: itemData.service,
            current_status: itemData.ticket_status,
          }).then((res) => {
            data = res.data.map(item => ({
              key: item.id,
              name: item.name,
            }));
          })
            .catch((res) => {
              errorHandler(res);
            });
        } else {
          data = [];
          itemData.choice.forEach((node) => {
            data.push({
              key: node.id,
              name: node.name,
            });
          });
        }
        break;
    }
    return data;
  }

  /**
   * Handle field selection and update related fields' relyOn values.
   */
  function itemSelect() {
    if (item.value.related_fields.be_relied) {
      item.value.related_fields.be_relied.forEach((fieldKey) => {
        fields.value.forEach((field) => {
          if (field.key === fieldKey) {
            field.relyOn[item.value.key] = item.value.val;
          }
        });
      });
    }
  }

  return {
    debounce,
    getFieldOptions,
    itemSelect,
  };
}
