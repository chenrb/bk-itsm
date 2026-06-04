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
        {{ $t('m.userManagement["用户管理"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <!-- 搜索过滤栏 -->
      <div class="bk-only-btn">
        <bk-button
          v-permission="'feature:system:user-manage'"
          theme="primary"
          icon="plus"
          :class="['mr10', 'plus-cus']"
          @click="openUserForm({}, 'new')">
          {{ $t('m.userManagement["新增用户"]') }}
        </bk-button>
        <div class="bk-only-search">
          <bk-input
            :clearable="true"
            :placeholder="labels.searchUser"
            right-icon="bk-icon icon-search"
            v-model="searchKeyword"
            @enter="getList(1)"
            @clear="getList(1)">
          </bk-input>
          <bk-select
            :clearable="true"
            :placeholder="labels.status"
            v-model="statusFilter"
            style="width: 140px; margin-left: 8px;"
            @change="getList(1)"
            @clear="getList(1)">
            <bk-option id="" :label="labels.all"></bk-option>
            <bk-option :id="true" :label="labels.active"></bk-option>
            <bk-option :id="false" :label="labels.disabled"></bk-option>
          </bk-select>
        </div>
      </div>

      <!-- 用户列表 -->
      <bk-table
        v-bkloading="{ isLoading: isDataLoading }"
        :data="tableList"
        :size="'small'"
        :pagination="pagination"
        @page-change="onPageChange"
        @page-limit-change="onPageLimitChange">
        <bk-table-column
          :label="labels.username"
          :show-overflow-tooltip="true"
          min-width="120">
          <template #default="props">
            <span>{{ props.row.username || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="labels.chname"
          :show-overflow-tooltip="true"
          min-width="120">
          <template #default="props">
            <span>{{ props.row.chname || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="labels.email"
          :show-overflow-tooltip="true"
          min-width="180">
          <template #default="props">
            <span>{{ props.row.email || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="labels.department"
          :show-overflow-tooltip="true"
          min-width="140">
          <template #default="props">
            <span>{{ props.row.department_name || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="labels.status"
          width="100">
          <template #default="props">
            <bk-tag :theme="props.row.is_active ? 'success' : 'danger'">
              {{ props.row.is_active ? $t('m.userManagement["启用"]') : $t('m.userManagement["停用"]') }}
            </bk-tag>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="labels.createdAt"
          width="180">
          <template #default="props">
            <span>{{ props.row.date_joined || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="labels.actions"
          width="220"
          fixed="right">
          <template #default="props">
            <bk-button
              v-permission="'feature:system:user-manage'"
              theme="primary"
              text
              @click="openUserForm(props.row, 'edit')">
              {{ $t('m.userManagement["编辑"]') }}
            </bk-button>
            <bk-button
              v-permission="'feature:system:user-manage'"
              theme="primary"
              text
              @click="openChangePassword(props.row)">
              {{ $t('m.userManagement["修改密码"]') }}
            </bk-button>
            <bk-button
              v-permission="'feature:system:user-manage'"
              v-if="props.row.is_active"
              theme="primary"
              text
              @click="toggleActive(props.row, false)">
              {{ $t('m.userManagement["停用"]') }}
            </bk-button>
            <bk-button
              v-permission="'feature:system:user-manage'"
              v-if="!props.row.is_active"
              theme="primary"
              text
              @click="toggleActive(props.row, true)">
              {{ $t('m.userManagement["启用"]') }}
            </bk-button>
            <bk-button
              v-permission="'feature:system:user-manage'"
              theme="primary"
              text
              @click="openResetPassword(props.row)">
              {{ $t('m.userManagement["重置密码"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>

    <!-- 用户表单 SideSlider -->
    <bk-sideslider
      :is-show="userFormConfig.isShow"
      :title="userFormConfig.title"
      :width="600"
      :quick-close="true"
      @update:isShow="userFormConfig.isShow = $event">
      <template #content>
        <user-form
          v-if="userFormConfig.isShow"
          :user-data="userFormConfig.data"
          :mode="userFormConfig.mode"
          @submit="onUserFormSubmit"
          @cancel="userFormConfig.isShow = false">
        </user-form>
      </template>
    </bk-sideslider>

    <!-- 修改密码 Dialog -->
    <bk-dialog
      v-model="changePwdDialog.isShow"
      :render-directive="'if'"
      :width="480"
      :loading="secondClick"
      :auto-close="false"
      :mask-close="false"
      @confirm="submitChangePassword"
      :title="labels.changePassword">
      <bk-form
        :label-width="120"
        form-type="vertical"
        ref="changePwdForm"
        :model="changePwdForm"
        :rules="changePwdRules">
        <bk-form-item :label="labels.oldPassword" :required="true" property="old_password">
          <bk-input v-model="changePwdForm.old_password" type="password" :show-password="true"></bk-input>
        </bk-form-item>
        <bk-form-item :label="labels.newPassword" :required="true" property="new_password">
          <bk-input v-model="changePwdForm.new_password" type="password" :show-password="true"></bk-input>
        </bk-form-item>
        <bk-form-item :label="labels.confirmPassword" :required="true" property="confirm_password">
          <bk-input v-model="changePwdForm.confirm_password" type="password" :show-password="true"></bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>

    <!-- 重置密码 Dialog -->
    <bk-dialog
      v-model="resetPwdDialog.isShow"
      :render-directive="'if'"
      :width="480"
      :loading="secondClick"
      :auto-close="false"
      :mask-close="false"
      @confirm="submitResetPassword"
      :title="labels.resetPassword">
      <bk-form
        :label-width="120"
        form-type="vertical"
        ref="resetPwdForm"
        :model="resetPwdForm"
        :rules="resetPwdRules">
        <bk-form-item :label="labels.newPassword" :required="true" property="new_password">
          <bk-input v-model="resetPwdForm.new_password" type="password" :show-password="true"></bk-input>
        </bk-form-item>
        <bk-form-item :label="labels.confirmPassword" :required="true" property="confirm_password">
          <bk-input v-model="resetPwdForm.confirm_password" type="password" :show-password="true"></bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
  import UserForm from './components/UserForm.vue';
  import { errorHandler } from '../../utils/errorHandler';

  export default {
    name: 'UserManagement',
    components: { UserForm },
    data() {
      return {
        secondClick: false,
        isDataLoading: false,
        tableList: [],
        // 搜索过滤
        searchKeyword: '',
        statusFilter: '',
        // 分页
        pagination: {
          current: 1,
          count: 0,
          limit: 10,
        },
        // 用户表单 SideSlider
        userFormConfig: {
          isShow: false,
          title: '',
          mode: 'new',
          data: {},
        },
        // 修改密码 Dialog
        changePwdDialog: { isShow: false, userId: null },
        changePwdForm: { old_password: '', new_password: '', confirm_password: '' },
        changePwdRules: {
          old_password: [{ required: true, message: this.$t('m.userManagement["请输入旧密码"]'), trigger: 'blur' }],
          new_password: [{ required: true, message: this.$t('m.userManagement["请输入新密码"]'), trigger: 'blur' }],
          confirm_password: [{
            required: true,
            message: this.$t('m.userManagement["请再次输入新密码"]'),
            trigger: 'blur',
          }, {
            validator: (val) => val === this.changePwdForm.new_password,
            message: this.$t('m.userManagement["两次输入的密码不一致"]'),
            trigger: 'blur',
          }],
        },
        // 重置密码 Dialog
        resetPwdDialog: { isShow: false, userId: null },
        resetPwdForm: { new_password: '', confirm_password: '' },
        resetPwdRules: {
          new_password: [{ required: true, message: this.$t('m.userManagement["请输入新密码"]'), trigger: 'blur' }],
          confirm_password: [{
            required: true,
            message: this.$t('m.userManagement["请再次输入新密码"]'),
            trigger: 'blur',
          }, {
            validator: (val) => val === this.resetPwdForm.new_password,
            message: this.$t('m.userManagement["两次输入的密码不一致"]'),
            trigger: 'blur',
          }],
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
          searchUser: t('m.userManagement["搜索用户"]'),
          status: t('m.userManagement["状态"]'),
          all: t('m.userManagement["全部"]'),
          active: t('m.userManagement["启用"]'),
          disabled: t('m.userManagement["停用"]'),
          username: t('m.userManagement["用户名"]'),
          chname: t('m.userManagement["中文名"]'),
          email: t('m.userManagement["邮箱"]'),
          department: t('m.userManagement["部门"]'),
          createdAt: t('m.userManagement["创建时间"]'),
          actions: t('m.userManagement["操作"]'),
          changePassword: t('m.userManagement["修改密码"]'),
          resetPassword: t('m.userManagement["重置密码"]'),
          oldPassword: t('m.userManagement["旧密码"]'),
          newPassword: t('m.userManagement["新密码"]'),
          confirmPassword: t('m.userManagement["确认密码"]'),
        };
      },
    },
    mounted() {
      this.getList();
    },
    methods: {
      getList(page) {
        this.isDataLoading = true;
        if (page) {
          this.pagination.current = page;
        }
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          search: this.searchKeyword,
        };
        if (this.statusFilter !== '' && this.statusFilter !== null && this.statusFilter !== undefined) {
          params.is_active = this.statusFilter;
        }
        this.$store.dispatch('userManagement/list', params).then((res) => {
          const data = res.data;
          this.tableList = data.results || data;
          this.pagination.count = data.count || 0;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
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
      // 用户表单
      openUserForm(row, mode) {
        this.userFormConfig.mode = mode;
        this.userFormConfig.data = { ...row };
        this.userFormConfig.title = mode === 'new'
          ? this.$t('m.userManagement["新增用户"]')
          : this.$t('m.userManagement["编辑用户"]');
        this.userFormConfig.isShow = true;
      },
      onUserFormSubmit(formData) {
        if (this.secondClick) return;
        this.secondClick = true;
        const action = this.userFormConfig.mode === 'new'
          ? 'userManagement/create'
          : 'userManagement/update';
        this.$store.dispatch(action, formData).then(() => {
          this.$bkMessage({
            message: this.userFormConfig.mode === 'new'
              ? this.$t('m.userManagement["新增用户"]') + ' ✓'
              : this.$t('m.userManagement["编辑用户"]') + ' ✓',
            theme: 'success',
          });
          this.userFormConfig.isShow = false;
          this.getList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 修改密码
      openChangePassword(row) {
        this.changePwdDialog.userId = row.id;
        this.changePwdForm = { old_password: '', new_password: '', confirm_password: '' };
        this.changePwdDialog.isShow = true;
      },
      submitChangePassword() {
        this.$refs.changePwdForm.validate().then(() => {
          if (this.secondClick) return;
          this.secondClick = true;
          this.$store.dispatch('userManagement/changePassword', {
            id: this.changePwdDialog.userId,
            old_password: this.changePwdForm.old_password,
            new_password: this.changePwdForm.new_password,
          }).then(() => {
            this.$bkMessage({
              message: this.$t('m.userManagement["修改密码"]') + ' ✓',
              theme: 'success',
            });
            this.changePwdDialog.isShow = false;
          })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        });
      },
      // 重置密码
      openResetPassword(row) {
        this.resetPwdDialog.userId = row.id;
        this.resetPwdForm = { new_password: '', confirm_password: '' };
        this.resetPwdDialog.isShow = true;
      },
      submitResetPassword() {
        this.$refs.resetPwdForm.validate().then(() => {
          if (this.secondClick) return;
          this.secondClick = true;
          this.$store.dispatch('userManagement/resetPassword', {
            id: this.resetPwdDialog.userId,
            new_password: this.resetPwdForm.new_password,
          }).then(() => {
            this.$bkMessage({
              message: this.$t('m.userManagement["重置密码"]') + ' ✓',
              theme: 'success',
            });
            this.resetPwdDialog.isShow = false;
          })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        });
      },
      // 启用/停用
      toggleActive(row, isActive) {
        const msg = isActive
          ? this.$t('m.userManagement["确认启用该用户？"]')
          : this.$t('m.userManagement["确认停用该用户？"]');
        this.$bkInfo({
          type: 'warning',
          title: msg,
          confirmFn: () => {
            this.$store.dispatch('userManagement/update', {
              id: row.id,
              is_active: isActive,
            }).then(() => {
              this.$bkMessage({
                message: isActive
                  ? this.$t('m.userManagement["启用"]') + ' ✓'
                  : this.$t('m.userManagement["停用"]') + ' ✓',
                theme: 'success',
              });
              this.getList();
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          },
        });
      },
    },
  };
</script>
