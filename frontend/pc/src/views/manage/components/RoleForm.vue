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
  <div style="padding: 24px 32px;">
    <!-- 基本信息 -->
    <h4 style="margin: 0 0 16px; font-size: 14px;">{{ $t('m.userManagement["基本信息"]') || '基本信息' }}</h4>
    <bk-form
      :label-width="120"
      form-type="vertical"
      :rules="rules"
      :model="formData"
      ref="roleForm">
      <bk-form-item :label="labels.roleName" :required="true" property="name">
        <bk-input v-model.trim="formData.name" maxlength="120" :placeholder="labels.placeholderRoleName"></bk-input>
      </bk-form-item>
      <bk-form-item :label="labels.roleKey" :required="true" property="role_key">
        <bk-input
          v-model.trim="formData.role_key"
          maxlength="64"
          :disabled="mode === 'edit'"
          :placeholder="labels.placeholderRoleKey">
        </bk-input>
      </bk-form-item>
      <bk-form-item :label="labels.roleDesc" property="desc">
        <bk-input v-model.trim="formData.desc" type="textarea" :rows="3" maxlength="255"></bk-input>
      </bk-form-item>
    </bk-form>

    <!-- 权限矩阵 -->
    <h4 style="margin: 24px 0 16px; font-size: 14px;">{{ $t('m.userManagement["权限矩阵"]') }}</h4>
    <div v-bkloading="{ isLoading: permLoading }">
      <div v-for="group in permissionGroups" :key="group.category" style="margin-bottom: 16px;">
        <div style="font-weight: bold; margin-bottom: 8px; padding: 4px 0; border-bottom: 1px solid #dcdee5;">
          {{ categoryLabel(group.category) }}
        </div>
        <div v-for="typeGroup in group.types" :key="typeGroup.type" style="margin-bottom: 4px; padding-left: 12px;">
          <span style="color: #979ba5; font-size: 12px; display: inline-block; width: 60px;">{{ typeLabel(typeGroup.type) }}</span>
          <bk-checkbox
            v-for="perm in typeGroup.items"
            :key="perm.code"
            v-model="perm._checked"
            style="margin-right: 16px; margin-bottom: 4px;">
            {{ perm.name }}
          </bk-checkbox>
        </div>
      </div>
    </div>

    <!-- 成员管理 -->
    <h4 style="margin: 24px 0 16px; font-size: 14px;">{{ $t('m.userManagement["成员管理"]') }}</h4>
    <bk-form :label-width="120" form-type="vertical">
      <bk-form-item :label="labels.members">
        <member-select v-model="formData.membersValue"></member-select>
      </bk-form-item>
      <bk-form-item :label="labels.owners">
        <member-select v-model="formData.ownersValue"></member-select>
      </bk-form-item>
    </bk-form>

    <!-- 操作按钮 -->
    <div style="margin-top: 24px; text-align: right;">
      <bk-button theme="default" @click="$emit('cancel')">
        {{ $t('m.common["取消"]') }}
      </bk-button>
      <bk-button theme="primary" style="margin-left: 8px;" @click="submitForm">
        {{ $t('m.common["确认"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import memberSelect from '@/views/commonComponent/memberSelect';

  export default {
    name: 'RoleForm',
    components: { memberSelect },
    props: {
      roleData: {
        type: Object,
        default: () => ({}),
      },
      mode: {
        type: String,
        default: 'new',
      },
    },
    data() {
      return {
        permLoading: false,
        permissionGroups: [],
        formData: {
          name: '',
          role_key: '',
          desc: '',
          membersValue: [],
          ownersValue: [],
        },
        rules: {
          name: [{ required: true, message: this.$t('m.userManagement["请输入角色名称"]'), trigger: 'blur' }],
          role_key: [{ required: true, message: this.$t('m.userManagement["请输入角色标识"]'), trigger: 'blur' }],
        },
      };
    },
    computed: {
      labels() {
        const t = this.$t.bind(this);
        return {
          roleName: t('m.userManagement["角色名称"]'),
          roleKey: t('m.userManagement["角色标识"]'),
          roleDesc: t('m.userManagement["角色描述"]'),
          placeholderRoleName: t('m.userManagement["请输入角色名称"]'),
          placeholderRoleKey: t('m.userManagement["请输入角色标识"]'),
          members: t('m.userManagement["成员"]'),
          owners: t('m.userManagement["负责人"]'),
        };
      },
    },
    mounted() {
      this.loadPermissions();
      if (this.mode === 'edit' && this.roleData.id) {
        this.formData = {
          id: this.roleData.id,
          name: this.roleData.name || '',
          role_key: this.roleData.role_key || '',
          desc: this.roleData.desc || '',
          membersValue: this.roleData.members || [],
          ownersValue: this.roleData.owners || [],
        };
      }
    },
    methods: {
      loadPermissions() {
        this.permLoading = true;
        this.$store.dispatch('roleManagement/permissions', { page_size: 200 }).then((res) => {
          const perms = res.data.results || res.data;
          // 角色已选权限
          const selectedCodes = new Set(this.roleData.permissions || []);
          // 按 category → type 分组
          const categoryMap = {};
          perms.forEach((p) => {
            if (!categoryMap[p.category]) {
              categoryMap[p.category] = {};
            }
            const cat = categoryMap[p.category];
            if (!cat[p.permission_type]) {
              cat[p.permission_type] = [];
            }
            cat[p.permission_type].push({
              ...p,
              _checked: selectedCodes.has(p.code),
            });
          });
          // 转为数组
          this.permissionGroups = Object.entries(categoryMap).map(([category, types]) => ({
            category,
            types: Object.entries(types).map(([type, items]) => ({
              type,
              items,
            })),
          }));
        })
          .finally(() => { this.permLoading = false; });
      },
      categoryLabel(category) {
        const map = {
          workflow: '流程管理',
          ticket: '工单管理',
          system: '系统管理',
          project: '项目管理',
          sla: 'SLA管理',
          task: '任务管理',
        };
        return this.$t(`m.userManagement["${map[category] || category}"]`) || map[category] || category;
      },
      typeLabel(type) {
        const map = {
          page: '页面',
          button: '按钮',
          feature: '功能',
        };
        return map[type] || type;
      },
      submitForm() {
        this.$refs.roleForm.validate().then(() => {
          // 收集选中的权限 codes
          const selectedPerms = [];
          this.permissionGroups.forEach((group) => {
            group.types.forEach((tg) => {
              tg.items.forEach((p) => {
                if (p._checked) selectedPerms.push(p.code);
              });
            });
          });
          const data = {
            name: this.formData.name,
            role_key: this.formData.role_key,
            desc: this.formData.desc,
            members: this.formData.membersValue,
            owners: this.formData.ownersValue,
            permissions: selectedPerms,
          };
          if (this.mode === 'edit') {
            data.id = this.formData.id;
          }
          this.$emit('submit', data);
        });
      },
    },
  };
</script>
