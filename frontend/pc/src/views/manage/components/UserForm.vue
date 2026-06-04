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
  <div class="user-form-wrapper" style="padding: 30px 40px;">
    <bk-form
      :label-width="120"
      form-type="vertical"
      :rules="rules"
      :model="formData"
      ref="userForm">
      <bk-form-item
        :label="labels.username"
        :required="true"
        property="username">
        <bk-input
          v-model.trim="formData.username"
          :disabled="mode === 'edit'"
          maxlength="64"
          :placeholder="labels.placeholderUsername">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        v-if="mode === 'new'"
        :label="labels.password"
        :required="true"
        property="password">
        <bk-input
          v-model="formData.password"
          type="password"
          :show-password="true"
          :placeholder="labels.placeholderPassword">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="labels.chname"
        property="chname">
        <bk-input
          v-model.trim="formData.chname"
          maxlength="64"
          :placeholder="labels.placeholderChname">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="labels.nickname"
        property="nickname">
        <bk-input v-model.trim="formData.nickname" maxlength="64"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="labels.email"
        property="email">
        <bk-input v-model.trim="formData.email" maxlength="128"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="labels.phone"
        property="phone">
        <bk-input v-model.trim="formData.phone" maxlength="20"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="labels.department"
        property="department">
        <bk-input v-model="formData.department_name" :disabled="true" :placeholder="labels.department"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="labels.leader"
        property="leader">
        <member-select
          v-model="formData.leaderValue"
          :multiple="false"
          :placeholder="labels.leader">
        </member-select>
      </bk-form-item>
    </bk-form>
    <div style="margin-top: 20px; text-align: right;">
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
    name: 'UserForm',
    components: { memberSelect },
    props: {
      userData: {
        type: Object,
        default: () => ({}),
      },
      mode: {
        type: String,
        default: 'new', // 'new' | 'edit'
      },
    },
    data() {
      return {
        formData: {
          username: '',
          password: '',
          chname: '',
          nickname: '',
          email: '',
          phone: '',
          department: '',
          department_name: '',
          leaderValue: [],
        },
        rules: {
          username: [{
            required: true,
            message: this.$t('m.userManagement["请输入用户名"]'),
            trigger: 'blur',
          }],
          password: [{
            required: true,
            message: this.$t('m.userManagement["请输入密码"]'),
            trigger: 'blur',
          }],
        },
      };
    },
    computed: {
      labels() {
        const t = this.$t.bind(this);
        return {
          username: t('m.userManagement["用户名"]'),
          password: t('m.userManagement["密码"]'),
          chname: t('m.userManagement["中文名"]'),
          nickname: t('m.userManagement["昵称"]'),
          email: t('m.userManagement["邮箱"]'),
          phone: t('m.userManagement["手机号"]'),
          department: t('m.userManagement["部门"]'),
          leader: t('m.userManagement["直属上级"]'),
          placeholderUsername: t('m.userManagement["请输入用户名"]'),
          placeholderPassword: t('m.userManagement["请输入密码"]'),
          placeholderChname: t('m.userManagement["请输入中文名"]'),
        };
      },
    },
    mounted() {
      if (this.mode === 'edit' && this.userData.id) {
        this.formData = {
          id: this.userData.id,
          username: this.userData.username || '',
          chname: this.userData.chname || '',
          nickname: this.userData.nickname || '',
          email: this.userData.email || '',
          phone: this.userData.phone || '',
          department: this.userData.department || '',
          department_name: this.userData.department_name || '',
          leaderValue: this.userData.leader ? [this.userData.leader] : [],
        };
      }
    },
    methods: {
      submitForm() {
        this.$refs.userForm.validate().then(() => {
          const data = { ...this.formData };
          // leader: member-select returns array of username strings
          if (data.leaderValue && data.leaderValue.length > 0) {
            const val = data.leaderValue[0];
            data.leader = typeof val === 'object' ? val.username : val;
          } else {
            data.leader = '';
          }
          delete data.leaderValue;
          delete data.department_name;
          if (this.mode === 'edit') {
            delete data.password;
          }
          this.$emit('submit', data);
        });
      },
    },
  };
</script>
