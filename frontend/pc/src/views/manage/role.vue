<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2025 Tencent.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div class="bk-itsm-service">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t('m.userManagement["角色管理"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-only-btn">
        <bk-button
          v-permission="'feature:system:role-manage'"
          theme="primary"
          icon="plus"
          :class="['mr10', 'plus-cus']"
          @click="openRoleForm({}, 'new')">
          {{ $t('m.userManagement["新增角色"]') }}
        </bk-button>
        <div class="bk-only-search">
          <bk-input
            :clearable="true"
            :placeholder="labels.searchRoleName"
            right-icon="bk-icon icon-search"
            v-model="searchName"
            @enter="getList(1)"
            @clear="getList(1)">
          </bk-input>
        </div>
      </div>

      <bk-table
        v-bkloading="{ isLoading: isDataLoading }"
        :data="tableList"
        :size="'small'"
        :pagination="pagination"
        @page-change="onPageChange"
        @page-limit-change="onPageLimitChange">
        <bk-table-column :label="labels.roleName" :show-overflow-tooltip="true" min-width="160">
          <template #default="props">
            <span>{{ props.row.name || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.roleKey" :show-overflow-tooltip="true" min-width="140">
          <template #default="props">
            <span>{{ props.row.role_key || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.builtinRole" width="100">
          <template #default="props">
            <bk-tag v-if="props.row.is_builtin" theme="info">{{ $t('m.userManagement["是"]') }}</bk-tag>
            <span v-else>{{ $t('m.userManagement["否"]') }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.memberCount" width="80">
          <template #default="props">
            <span>{{ props.row.members_count || (props.row.members ? props.row.members.length : 0) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.permCount" width="80">
          <template #default="props">
            <span>{{ props.row.permissions_count || (props.row.permissions ? props.row.permissions.length : 0) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.actions" width="150" fixed="right">
          <template #default="props">
            <bk-button
              v-permission="'feature:system:role-manage'"
              theme="primary"
              text
              @click="openRoleForm(props.row, 'edit')">
              {{ $t('m.userManagement["编辑"]') }}
            </bk-button>
            <bk-button
              v-permission="'feature:system:role-manage'"
              v-if="!props.row.is_builtin"
              theme="primary"
              text
              @click="deleteRole(props.row)">
              {{ $t('m.userManagement["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>

    <!-- 角色表单 SideSlider -->
    <bk-sideslider
      :is-show="roleFormConfig.isShow"
      :title="roleFormConfig.title"
      :width="780"
      :quick-close="true"
      @update:isShow="roleFormConfig.isShow = $event">
      <template #content>
        <role-form
          v-if="roleFormConfig.isShow"
          :role-data="roleFormConfig.data"
          :mode="roleFormConfig.mode"
          @submit="onRoleFormSubmit"
          @cancel="roleFormConfig.isShow = false">
        </role-form>
      </template>
    </bk-sideslider>
  </div>
</template>

<script>
  import RoleForm from './components/RoleForm.vue';
  import { errorHandler } from '../../utils/errorHandler';

  export default {
    name: 'RoleManagement',
    components: { RoleForm },
    data() {
      return {
        isDataLoading: false,
        searchName: '',
        tableList: [],
        pagination: { current: 1, count: 0, limit: 10 },
        roleFormConfig: {
          isShow: false,
          title: '',
          mode: 'new',
          data: {},
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      labels() {
        const t = this.$t.bind(this);
        return {
          searchRoleName: t('m.userManagement["请输入角色名称"]'),
          roleName: t('m.userManagement["角色名称"]'),
          roleKey: t('m.userManagement["角色标识"]'),
          builtinRole: t('m.userManagement["内置角色"]'),
          memberCount: t('m.userManagement["成员数"]'),
          permCount: t('m.userManagement["权限数"]'),
          actions: t('m.userManagement["操作"]'),
        };
      },
    },
    mounted() {
      this.getList();
    },
    methods: {
      getList(page) {
        this.isDataLoading = true;
        if (page) this.pagination.current = page;
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          search: this.searchName,
        };
        this.$store.dispatch('roleManagement/list', params).then((res) => {
          const data = res.data;
          this.tableList = data.results || data;
          this.pagination.count = data.count || 0;
        })
          .catch((res) => { errorHandler(res, this); })
          .finally(() => { this.isDataLoading = false; });
      },
      onPageChange(page) {
        this.pagination.current = page;
        this.getList();
      },
      onPageLimitChange(limit) {
        this.pagination.limit = limit;
        this.pagination.current = 1;
        this.getList();
      },
      openRoleForm(row, mode) {
        this.roleFormConfig.mode = mode;
        this.roleFormConfig.data = { ...row };
        this.roleFormConfig.title = mode === 'new'
          ? this.$t('m.userManagement["新增角色"]')
          : this.$t('m.userManagement["编辑角色"]');
        this.roleFormConfig.isShow = true;
      },
      onRoleFormSubmit(formData) {
        const action = this.roleFormConfig.mode === 'new'
          ? 'roleManagement/create'
          : 'roleManagement/update';
        this.$store.dispatch(action, formData).then(() => {
          this.$bkMessage({
            message: this.roleFormConfig.mode === 'new'
              ? this.$t('m.userManagement["新增角色"]') + ' ✓'
              : this.$t('m.userManagement["编辑角色"]') + ' ✓',
            theme: 'success',
          });
          this.roleFormConfig.isShow = false;
          this.getList();
        })
          .catch((res) => { errorHandler(res, this); });
      },
      deleteRole(row) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.userManagement["确认删除该角色？"]'),
          confirmFn: () => {
            this.$store.dispatch('roleManagement/delete', row.id).then(() => {
              this.$bkMessage({
                message: this.$t('m.userManagement["删除"]') + ' ✓',
                theme: 'success',
              });
              this.getList();
            })
              .catch((res) => { errorHandler(res, this); });
          },
        });
      },
    },
  };
</script>
