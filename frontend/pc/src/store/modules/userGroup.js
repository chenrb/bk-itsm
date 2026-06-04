/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2025 Tencent.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 */

import ajax from '../../utils/ajax';

export default {
  namespaced: true,
  state: {
    groupList: [],
  },
  mutations: {
    setGroupList(state, list) {
      state.groupList = list;
    },
  },
  actions: {
    list({ commit, state, dispatch }, params) {
      return ajax.get('user-groups/', { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    create({ commit, state, dispatch }, data) {
      return ajax.post('user-groups/', data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, data) {
      return ajax.patch(`user-groups/${data.id}/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delete({ commit, state, dispatch }, id) {
      return ajax.delete(`user-groups/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
