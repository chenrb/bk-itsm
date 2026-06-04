/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2025 Tencent.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 */

import ajax from '../../utils/ajax';

export default {
  namespaced: true,
  state: {
    departmentList: [],
  },
  mutations: {
    setDepartmentList(state, list) {
      state.departmentList = list;
    },
  },
  actions: {
    tree({ commit, state, dispatch }, params) {
      return ajax.get('departments/', { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    create({ commit, state, dispatch }, data) {
      return ajax.post('departments/', data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, data) {
      return ajax.patch(`departments/${data.id}/`, data).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delete({ commit, state, dispatch }, id) {
      return ajax.delete(`departments/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    members({ commit, state, dispatch }, params) {
      const id = params.id;
      delete params.id;
      return ajax.get(`departments/${id}/members/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
