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
import { useRoute } from 'vue-router';
import bus from '@/utils/bus.js';

/**
 * Permission composable - handles permission checking and application.
 *
 * Uses Vuex store and vue-router internally.
 */
export function usePermission() {
  const store = useStore();
  const route = useRoute();

  /**
   * Get all app-level permissions (project permissions + non-resource page permissions).
   * @param {Array} curPermission - Current instance-level permissions
   * @returns {Array} Combined permission list
   */
  function getAllAppPermission(curPermission) {
    const { systemPermission } = store.state.common;
    return [...systemPermission, ...curPermission];
  }

  /**
   * Check if the required permissions are satisfied.
   * @param {Array} reqPermission - Required permissions
   * @param {Array} curPermission - Current permissions
   * @returns {Boolean}
   */
  function hasPermission(reqPermission = [], curPermission = []) {
    const { actions } = store.state.common.permissionMeta;
    return reqPermission.every((item) => {
      const permActionData = actions.find(action => action.id === item);
      if (!permActionData) {
        return false;
      }
      if (!getAllAppPermission(curPermission).includes(item)) {
        return false;
      }
      if (permActionData.relate_actions.length > 0) {
        return hasPermission(permActionData.relate_actions, curPermission);
      }
      return true;
    });
  }

  /**
   * Assemble permission application data for redirect.
   * @param {Array} reqPermission - Required permissions
   * @param {Array} curPermission - Current permissions
   * @param {Object} resourceData - Resource data
   * @param {Boolean} ret - If true, return data instead of triggering modal
   * @returns {Object|undefined}
   */
  function applyForPermission(reqPermission = [], curPermission = [], resourceData = {}, ret = false) {
    const { actions, resources, system } = store.state.common.permissionMeta;
    const bkitsm = system[0];
    const { id: systemId, name: systemName } = bkitsm;
    const actionsData = assembleActionsData(
      reqPermission,
      curPermission,
      resourceData,
      actions,
      resources,
      systemId,
      systemName
    );
    const data = {
      system_id: systemId,
      system_name: systemName,
      actions: actionsData,
    };
    if (ret) {
      return data;
    }
    triggerPermisionModal(data);
  }

  /**
   * Assemble actions data. Recursively handles permission dependencies.
   */
  function assembleActionsData(reqPermission, curPermission, resourceData, actions, resources, systemId, systemName) {
    const actionsData = [];
    reqPermission.forEach((requiredItem) => {
      const permActionData = actions.find(action => action.id === requiredItem);
      if (!permActionData) {
        return;
      }
      if (!getAllAppPermission(curPermission).includes(requiredItem)) {
        const relateResources = [];
        permActionData.relate_resources.forEach((reItem) => {
          const resourceMap = resources.find(item => item.id === reItem);
          const instances = assembleInstances(resources, resourceMap, resourceData);
          relateResources.push({
            system_id: systemId,
            system_name: systemName,
            type: resourceMap.id,
            type_name: resourceMap.name,
            instances: [instances],
          });
        });
        actionsData.push({
          id: permActionData.id,
          name: permActionData.name,
          related_resource_types: relateResources,
        });
      }
      if (permActionData.relate_actions.length > 0) {
        const relateActions = assembleActionsData(
          permActionData.relate_actions,
          curPermission,
          resourceData,
          actions,
          resources,
          systemId,
          systemName
        );
        relateActions.forEach((item) => {
          if (actionsData.findIndex(action => action.id === item.id) === -1) {
            actionsData.push(item);
          }
        });
      }
    });
    return actionsData;
  }

  /**
   * Assemble resource instances for permissions.
   */
  function assembleInstances(resources, resourceMap, resourceData) {
    let data = [];
    if (resourceMap.parent_id) {
      const parentMap = resources.find(item => item.id === resourceMap.parent_id);
      data = data.concat(assembleInstances(resources, parentMap, resourceData));
    }
    const instanceData = resourceData[resourceMap.id];
    instanceData.forEach((item) => {
      data.push({
        type: resourceMap.id,
        type_name: resourceMap.name,
        id: item.id,
        name: item.name,
      });
    });
    return data;
  }

  /**
   * Open the permission application modal.
   * @param {Object} permissions - Permission data for the modal
   */
  function triggerPermisionModal(permissions) {
    bus.$emit('showPermissionModal', permissions);
  }

  /**
   * Check page-level permission based on route name.
   * @returns {Object} { verified: Boolean, data: Object|null }
   */
  function checkPagePermission() {
    const authMap = {
      OperationHome: 'operational_data_view',
      OperationService: 'operational_data_view',
      notifySetting: 'notification_view',
      slaPriority: 'sla_priority_view',
      ticketStatus: 'ticket_state_view',
      globalSetting: 'global_settings_view',
    };
    const actionId = authMap[route.name];

    if (actionId && !hasPermission([actionId])) {
      const data = applyForPermission([actionId], [], {}, true);
      return { verified: false, data };
    }

    return { verified: true, data: null };
  }

  return {
    getAllAppPermission,
    hasPermission,
    applyForPermission,
    assembleActionsData,
    assembleInstances,
    triggerPermisionModal,
    checkPagePermission,
  };
}
