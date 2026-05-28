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
import { useI18n } from 'vue-i18n';
import { errorHandler } from '@/utils/errorHandler';
import { deepClone } from '@/utils/util';

/**
 * Ticket list async data loading composable.
 *
 * Provides methods for asynchronously replacing ticket list attributes
 * (processors, creators, can_operate status).
 */
export function useTicketList() {
  const store = useStore();
  const { t } = useI18n();

  /**
   * Async load certain field info in ticket list.
   * @param {Array} originList - Ticket list
   */
  function asyncReplaceTicketListAttr(originList) {
    if (originList.length === 0) {
      return;
    }
    getTicketsProcessors(originList);
    getTicketsCreator(originList);
    getTicketscanOperate(originList);
  }

  /**
   * Async get ticket processors.
   * @param {Array} originList - Ticket list
   */
  function getTicketsProcessors(originList) {
    const copyList = deepClone(originList);
    const loadingText = t('m.manageCommon[\'加载中...\']');
    originList.forEach((ticket) => {
      ticket['current_processors'] = loadingText;
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
    })
      .catch((res) => {
        errorHandler(res);
      });
  }

  /**
   * Async get ticket creators.
   * @param {Array} originList - Ticket list
   */
  function getTicketsCreator(originList) {
    const copyList = deepClone(originList);
    const loadingText = t('m.manageCommon[\'加载中...\']');
    originList.forEach((ticket) => {
      ticket['creator'] = loadingText;
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

  /**
   * Async get ticket can_operate status.
   * @param {Array} originList - Ticket list
   */
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

  return {
    asyncReplaceTicketListAttr,
    getTicketsProcessors,
    getTicketsCreator,
    getTicketscanOperate,
  };
}
