/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2025 Tencent.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 */

import ajax from '../../utils/ajax';

export default {
  namespaced: true,
  state: {
    userList: [],
    userListLoading: false,
  },
  mutations: {
    setUserList(state, list) {
      state.userList = list;
    },
    setUserListLoading(state, loading) {
      state.userListLoading = loading;
    },
  },
  actions: {
    list({ commit, state, dispatch }, params) {
      commit('setUserListLoading', true);
      return ajax.get('users/', { params }).then((response) => {
        const res = response.data;
        commit('setUserList', res.data.results || res.data);
        return res;
      }).catch((err) => {
        return Promise.reject(err);
      }).finally(() => {
        commit('setUserListLoading', false);
      });
    },
    create({ commit, state, dispatch }, data) {
      return ajax.post('users/', data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, data) {
      return ajax.patch(`users/${data.id}/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    changePassword({ commit, state, dispatch }, data) {
      return ajax.post(`users/${data.id}/change_password/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    resetPassword({ commit, state, dispatch }, data) {
      return ajax.post(`users/${data.id}/reset_password/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
