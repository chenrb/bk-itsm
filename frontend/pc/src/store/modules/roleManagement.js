/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2025 Tencent.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 */

import ajax from '../../utils/ajax';

export default {
  namespaced: true,
  state: {
    roleList: [],
    permissionList: [],
  },
  mutations: {
    setRoleList(state, list) {
      state.roleList = list;
    },
    setPermissionList(state, list) {
      state.permissionList = list;
    },
  },
  actions: {
    list({ commit, state, dispatch }, params) {
      return ajax.get('roles/', { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    create({ commit, state, dispatch }, data) {
      return ajax.post('roles/', data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, data) {
      return ajax.patch(`roles/${data.id}/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delete({ commit, state, dispatch }, id) {
      return ajax.delete(`roles/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    permissions({ commit, state, dispatch }, params) {
      return ajax.get('permissions/', { params }).then((response) => {
        const res = response.data;
        commit('setPermissionList', res.data.results || res.data);
        return res;
      });
    },
  },
};
