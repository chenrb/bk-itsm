/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2025 Tencent.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 */

import ajax from '../../utils/ajax';

export default {
  namespaced: true,
  state: {
    policyList: [],
    lockedAccounts: [],
  },
  mutations: {
    setPolicyList(state, list) {
      state.policyList = list;
    },
    setLockedAccounts(state, list) {
      state.lockedAccounts = list;
    },
  },
  actions: {
    list({ commit, state, dispatch }, params) {
      return ajax.get('security-policies/', { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, data) {
      return ajax.patch(`security-policies/${data.id}/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    unlock({ commit, state, dispatch }, data) {
      return ajax.post('security-policies/unlock/', data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    lockedAccounts({ commit, state, dispatch }, params) {
      return ajax.get('security-policies/locked_accounts/', { params }).then((response) => {
        const res = response.data;
        commit('setLockedAccounts', res.data.results || res.data);
        return res;
      });
    },
  },
};
