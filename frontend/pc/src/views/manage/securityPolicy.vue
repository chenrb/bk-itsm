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
        {{ $t('m.userManagement["安全策略"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <bk-tab :active.sync="activeTab" type="card">
        <bk-tab-panel
          v-for="tab in tabs"
          :key="tab.name"
          :name="tab.name"
          :label="tab.label">
          <!-- 密码/登录/会话策略 -->
          <template v-if="tab.name !== 'locked'">
            <bk-table
              v-bkloading="{ isLoading: policyLoading }"
              :data="tabPolicies(tab.name)"
              :size="'small'">
              <bk-table-column :label="labels.policyName" min-width="200">
                <template #default="props">
                  <span>{{ props.row.description || props.row.key }}</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="labels.currentValue" width="200">
                <template #default="props">
                  <span>{{ formatValue(props.row.value) }}</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="labels.actions" width="100">
                <template #default="props">
                  <bk-button
                    v-permission="'feature:system:security-manage'"
                    theme="primary"
                    text
                    @click="openEditDialog(props.row)">
                    {{ $t('m.userManagement["修改策略"]') }}
                  </bk-button>
                </template>
              </bk-table-column>
            </bk-table>
          </template>

          <!-- 锁定账户 Tab -->
          <template v-if="tab.name === 'locked'">
            <bk-table
              v-bkloading="{ isLoading: lockedLoading }"
              :data="lockedAccounts"
              :size="'small'">
              <bk-table-column :label="labels.username" min-width="120">
                <template #default="props">
                  <span>{{ props.row.username || '--' }}</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="labels.ipAddress" min-width="140">
                <template #default="props">
                  <span>{{ props.row.ip_address || '--' }}</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="labels.loginAttempts" width="100">
                <template #default="props">
                  <span>{{ props.row.attempts }}</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="labels.lockedTime" width="180">
                <template #default="props">
                  <span>{{ props.row.locked_until || '--' }}</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="labels.actions" width="100">
                <template #default="props">
                  <bk-button
                    v-permission="'feature:system:security-manage'"
                    theme="primary"
                    text
                    @click="unlockAccount(props.row)">
                    {{ $t('m.userManagement["解锁"]') }}
                  </bk-button>
                </template>
              </bk-table-column>
            </bk-table>
          </template>
        </bk-tab-panel>
      </bk-tab>
    </div>

    <!-- 策略编辑 Dialog -->
    <bk-dialog
      v-model="editDialog.isShow"
      :render-directive="'if'"
      :width="400"
      :auto-close="false"
      :mask-close="false"
      @confirm="submitEdit"
      :title="labels.editPolicy">
      <bk-form form-type="vertical" ref="editForm">
        <bk-form-item :label="editDialog.description">
          <bk-switcher
            v-if="editDialog.valueType === 'boolean'"
            v-model="editDialog.boolValue"
            theme="primary">
          </bk-switcher>
          <bk-input
            v-else
            v-model.number="editDialog.numValue"
            type="number"
            :min="editDialog.minValue || 0">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';

  export default {
    name: 'SecurityPolicy',
    data() {
      return {
        activeTab: 'password',
        policyLoading: false,
        lockedLoading: false,
        policies: [],
        lockedAccounts: [],
        tabs: [
          { name: 'password', label: this.$t('m.userManagement["密码策略"]') },
          { name: 'login', label: this.$t('m.userManagement["登录策略"]') },
          { name: 'session', label: this.$t('m.userManagement["会话策略"]') },
          { name: 'locked', label: this.$t('m.userManagement["锁定账户"]') },
        ],
        editDialog: {
          isShow: false,
          id: null,
          key: '',
          description: '',
          valueType: 'number',
          boolValue: false,
          numValue: 0,
          minValue: 0,
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
          policyName: t('m.userManagement["策略名称"]'),
          currentValue: t('m.userManagement["当前值"]'),
          actions: t('m.userManagement["操作"]'),
          username: t('m.userManagement["用户名"]'),
          ipAddress: t('m.userManagement["IP地址"]'),
          loginAttempts: t('m.userManagement["登录次数"]'),
          lockedTime: t('m.userManagement["锁定时间"]'),
          editPolicy: t('m.userManagement["修改策略"]'),
        };
      },
    },
    watch: {
      activeTab(val) {
        if (val === 'locked') {
          this.loadLockedAccounts();
        }
      },
    },
    mounted() {
      this.loadPolicies();
    },
    methods: {
      tabPolicies(category) {
        return this.policies.filter(p => p.category === category);
      },
      formatValue(value) {
        if (typeof value === 'boolean') {
          return value ? this.$t('m.userManagement["是"]') : this.$t('m.userManagement["否"]');
        }
        return String(value);
      },
      loadPolicies() {
        this.policyLoading = true;
        this.$store.dispatch('securityPolicy/list', { page_size: 100 }).then((res) => {
          this.policies = res.data.results || res.data;
        })
          .catch((res) => { errorHandler(res, this); })
          .finally(() => { this.policyLoading = false; });
      },
      loadLockedAccounts() {
        this.lockedLoading = true;
        this.$store.dispatch('securityPolicy/lockedAccounts').catch((res) => {
          errorHandler(res, this);
        }).finally(() => { this.lockedLoading = false; });
      },
      openEditDialog(row) {
        this.editDialog = {
          isShow: true,
          id: row.id,
          key: row.key,
          description: row.description || row.key,
          valueType: typeof row.value,
          boolValue: row.value === true,
          numValue: typeof row.value === 'number' ? row.value : 0,
          minValue: row.key.includes('length') ? 6 : 0,
        };
      },
      submitEdit() {
        const newValue = this.editDialog.valueType === 'boolean'
          ? this.editDialog.boolValue
          : this.editDialog.numValue;
        this.$store.dispatch('securityPolicy/update', {
          id: this.editDialog.id,
          value: newValue,
        }).then(() => {
          this.$bkMessage({
            message: this.$t('m.userManagement["修改策略"]') + ' ✓',
            theme: 'success',
          });
          this.editDialog.isShow = false;
          this.loadPolicies();
        })
          .catch((res) => { errorHandler(res, this); });
      },
      unlockAccount(row) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.userManagement["确认解锁该账户？"]'),
          subTitle: this.$t('m.userManagement["解锁后用户可以正常登录"]'),
          confirmFn: () => {
            this.$store.dispatch('securityPolicy/unlock', {
              username: row.username,
            }).then(() => {
              this.$bkMessage({
                message: this.$t('m.userManagement["解锁"]') + ' ✓',
                theme: 'success',
              });
              this.loadLockedAccounts();
            })
              .catch((res) => { errorHandler(res, this); });
          },
        });
      },
    },
  };
</script>
