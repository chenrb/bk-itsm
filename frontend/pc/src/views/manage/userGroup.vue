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
        {{ $t('m.userManagement["角色组管理"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-only-btn">
        <bk-button
          v-permission="'feature:system:group-manage'"
          theme="primary"
          icon="plus"
          :class="['mr10', 'plus-cus']"
          @click="openForm({}, 'new')">
          {{ $t('m.userManagement["新增角色组"]') }}
        </bk-button>
        <div class="bk-only-search">
          <bk-input
            :clearable="true"
            :placeholder="labels.searchGroupName"
            right-icon="bk-icon icon-search"
            v-model="searchName"
            @enter="getList(1)"
            @clear="getList(1)">
          </bk-input>
          <bk-select
            :clearable="true"
            v-model="builtinFilter"
            style="width: 140px; margin-left: 8px;"
            @change="getList(1)"
            @clear="getList(1)">
            <bk-option id="" :label="labels.all"></bk-option>
            <bk-option :id="true" :label="labels.builtinGroup"></bk-option>
            <bk-option :id="false" :label="labels.no"></bk-option>
          </bk-select>
        </div>
      </div>

      <bk-table
        v-bkloading="{ isLoading: isDataLoading }"
        :data="tableList"
        :size="'small'"
        :pagination="pagination"
        @page-change="onPageChange"
        @page-limit-change="onPageLimitChange">
        <bk-table-column :label="labels.groupName" :show-overflow-tooltip="true" min-width="160">
          <template #default="props">
            <span>{{ props.row.name || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.groupKey" :show-overflow-tooltip="true" min-width="140">
          <template #default="props">
            <span>{{ props.row.group_key || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.builtinGroup" width="100">
          <template #default="props">
            <bk-tag v-if="props.row.is_builtin" theme="info">{{ $t('m.userManagement["是"]') }}</bk-tag>
            <span v-else>{{ $t('m.userManagement["否"]') }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.memberCount" width="80">
          <template #default="props">
            <span>{{ props.row.members ? props.row.members.length : 0 }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.owners" :show-overflow-tooltip="true" min-width="140">
          <template #default="props">
            <span>{{ props.row.owners && props.row.owners.length ? props.row.owners.join(', ') : '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="labels.actions" width="150" fixed="right">
          <template #default="props">
            <bk-button
              v-permission="'feature:system:group-manage'"
              theme="primary"
              text
              @click="openForm(props.row, 'edit')">
              {{ $t('m.userManagement["编辑"]') }}
            </bk-button>
            <bk-button
              v-permission="'feature:system:group-manage'"
              v-if="!props.row.is_builtin"
              theme="primary"
              text
              @click="deleteGroup(props.row)">
              {{ $t('m.userManagement["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>

    <!-- 角色组表单 Dialog -->
    <bk-dialog
      v-model="formDialog.isShow"
      :render-directive="'if'"
      :width="700"
      :loading="secondClick"
      :auto-close="false"
      :mask-close="false"
      @confirm="submitForm"
      :title="formDialog.mode === 'new' ? labels.addGroup : labels.editGroup">
      <bk-form
        :label-width="200"
        form-type="vertical"
        :rules="formRules"
        :model="formData"
        ref="groupForm">
        <bk-form-item :label="labels.groupName" :required="true" property="name">
          <bk-input v-model.trim="formData.name" maxlength="120" :placeholder="labels.placeholderGroupName"></bk-input>
        </bk-form-item>
        <bk-form-item :label="labels.groupKey" :required="true" property="group_key">
          <bk-input
            v-model.trim="formData.group_key"
            maxlength="64"
            :disabled="formDialog.mode === 'edit'"
            :placeholder="labels.placeholderGroupKey">
          </bk-input>
        </bk-form-item>
        <bk-form-item :label="labels.groupDesc" property="desc">
          <bk-input v-model.trim="formData.desc" type="textarea" :rows="3" maxlength="255"></bk-input>
        </bk-form-item>
        <bk-form-item :label="labels.members">
          <member-select v-model="formData.membersValue"></member-select>
        </bk-form-item>
        <bk-form-item :label="labels.owners">
          <member-select v-model="formData.ownersValue"></member-select>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
  import memberSelect from '@/views/commonComponent/memberSelect';
  import { errorHandler } from '../../utils/errorHandler';

  export default {
    name: 'UserGroupManagement',
    components: { memberSelect },
    data() {
      return {
        secondClick: false,
        isDataLoading: false,
        searchName: '',
        builtinFilter: '',
        tableList: [],
        pagination: { current: 1, count: 0, limit: 10 },
        formDialog: { isShow: false, mode: 'new' },
        formData: {
          name: '',
          group_key: '',
          desc: '',
          membersValue: [],
          ownersValue: [],
        },
        formRules: {
          name: [{ required: true, message: this.$t('m.userManagement["请输入角色组名称"]'), trigger: 'blur' }],
          group_key: [{ required: true, message: this.$t('m.userManagement["请输入角色组标识"]'), trigger: 'blur' }],
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
          searchGroupName: t('m.userManagement["请输入角色组名称"]'),
          all: t('m.userManagement["全部"]'),
          builtinGroup: t('m.userManagement["内置角色组"]'),
          no: t('m.userManagement["否"]'),
          groupName: t('m.userManagement["角色组名称"]'),
          groupKey: t('m.userManagement["角色组标识"]'),
          groupDesc: t('m.userManagement["角色组描述"]'),
          memberCount: t('m.userManagement["成员数"]'),
          owners: t('m.userManagement["负责人"]'),
          actions: t('m.userManagement["操作"]'),
          members: t('m.userManagement["成员"]'),
          placeholderGroupName: t('m.userManagement["请输入角色组名称"]'),
          placeholderGroupKey: t('m.userManagement["请输入角色组标识"]'),
          addGroup: t('m.userManagement["新增角色组"]'),
          editGroup: t('m.userManagement["编辑角色组"]'),
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
        if (this.builtinFilter !== '' && this.builtinFilter !== null && this.builtinFilter !== undefined) {
          params.is_builtin = this.builtinFilter;
        }
        this.$store.dispatch('userGroup/list', params).then((res) => {
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
      openForm(row, mode) {
        this.formDialog.mode = mode;
        this.formData = {
          id: row.id || null,
          name: row.name || '',
          group_key: row.group_key || '',
          desc: row.desc || '',
          membersValue: row.members || [],
          ownersValue: row.owners || [],
        };
        this.formDialog.isShow = true;
      },
      submitForm() {
        this.$refs.groupForm.validate().then(() => {
          if (this.secondClick) return;
          this.secondClick = true;
          const data = {
            name: this.formData.name,
            group_key: this.formData.group_key,
            desc: this.formData.desc,
            members: this.formData.membersValue,
            owners: this.formData.ownersValue,
          };
          const action = this.formDialog.mode === 'new' ? 'userGroup/create' : 'userGroup/update';
          if (this.formDialog.mode === 'edit') data.id = this.formData.id;
          this.$store.dispatch(action, data).then(() => {
            this.$bkMessage({
              message: this.formDialog.mode === 'new'
                ? this.$t('m.userManagement["新增角色组"]') + ' ✓'
                : this.$t('m.userManagement["编辑角色组"]') + ' ✓',
              theme: 'success',
            });
            this.formDialog.isShow = false;
            this.getList();
          })
            .catch((res) => { errorHandler(res, this); })
            .finally(() => { this.secondClick = false; });
        });
      },
      deleteGroup(row) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.userManagement["确认删除该角色组？"]'),
          confirmFn: () => {
            this.$store.dispatch('userGroup/delete', row.id).then(() => {
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
