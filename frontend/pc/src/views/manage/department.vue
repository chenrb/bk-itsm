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
        {{ $t('m.userManagement["部门管理"]') }}
      </p>
    </div>
    <div class="itsm-page-content" style="display: flex; gap: 16px;">
      <!-- 左侧：部门树 -->
      <div style="width: 300px; min-width: 300px; border: 1px solid #dcdee5; border-radius: 2px; padding: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span style="font-weight: bold;">{{ $t('m.userManagement["部门名称"]') }}</span>
          <bk-button
            v-permission="'feature:system:department-manage'"
            theme="primary"
            text
            icon="plus"
            @click="openDeptForm({}, 'new', null)">
          </bk-button>
        </div>
        <div style="max-height: 500px; overflow: auto;">
          <div v-for="node in treeData" :key="node.id" class="dept-tree-node">
            <div
              class="dept-node-content"
              :class="{ 'dept-node-selected': selectedNode && selectedNode.id === node.id }"
              @click="selectNode(node)">
              <span
                class="bk-icon dept-expand-icon"
                :class="node._expanded ? 'icon-down-shape' : 'icon-right-shape'"
                v-if="node.has_children || (node.children && node.children.length > 0)"
                @click.stop="toggleNode(node)">
              </span>
              <span class="dept-expand-placeholder" v-else></span>
              <span class="dept-node-name" :title="node.name">{{ node.name }}</span>
              <span class="dept-node-actions" v-permission="'feature:system:department-manage'">
                <i class="bk-icon icon-plus" @click.stop="openDeptForm({}, 'new', node)" style="cursor: pointer; font-size: 14px;"></i>
                <i class="bk-icon icon-edit" @click.stop="openDeptForm(node, 'edit', null)" style="cursor: pointer; font-size: 14px; margin-left: 4px;"></i>
              </span>
            </div>
            <div v-if="node._expanded && node.children && node.children.length > 0" style="padding-left: 20px;">
              <dept-sub-tree
                :nodes="node.children"
                :selected-node="selectedNode"
                @select="selectNode"
                @toggle="toggleNode"
                @add="openDeptForm"
                @edit="openDeptForm">
              </dept-sub-tree>
            </div>
          </div>
          <div v-if="treeData.length === 0 && !treeLoading" style="text-align: center; color: #979ba5; padding: 20px;">
            {{ $t('m.userManagement["新建根部门"]') }}
          </div>
        </div>
      </div>

      <!-- 右侧：部门详情 & 成员列表 -->
      <div style="flex: 1; min-width: 0;">
        <template v-if="selectedNode">
          <div style="margin-bottom: 16px;">
            <h3 style="margin: 0 0 8px;">{{ selectedNode.name }}</h3>
            <span style="color: #979ba5;">
              {{ $t('m.userManagement["成员列表"]') }}（{{ memberPagination.count }}）
            </span>
          </div>
          <bk-table
            v-bkloading="{ isLoading: memberLoading }"
            :data="memberList"
            :size="'small'"
            :pagination="memberPagination"
            @page-change="onMemberPageChange"
            @page-limit-change="onMemberPageLimitChange">
            <bk-table-column :label="labelMap.chname" :show-overflow-tooltip="true" min-width="120">
              <template #default="props">
                <span>{{ props.row.chname || '--' }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="labelMap.username" :show-overflow-tooltip="true" min-width="120">
              <template #default="props">
                <span>{{ props.row.username || '--' }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="labelMap.isPrimary" width="120">
              <template #default="props">
                <bk-tag :theme="props.row.is_primary ? 'success' : ''">
                  {{ props.row.is_primary ? $t('m.userManagement["是"]') : $t('m.userManagement["否"]') }}
                </bk-tag>
              </template>
            </bk-table-column>
          </bk-table>
        </template>
        <template v-else>
          <div style="text-align: center; color: #979ba5; padding: 60px 0;">
            {{ $t('m.userManagement["请选择部门"]') }}
          </div>
        </template>
      </div>
    </div>

    <!-- 部门表单 Dialog -->
    <bk-dialog
      v-model="deptDialog.isShow"
      :render-directive="'if'"
      :width="480"
      :loading="secondClick"
      :auto-close="false"
      :mask-close="false"
      @confirm="submitDept"
      :title="deptDialog.mode === 'new' ? dialogTitleNew : dialogTitleEdit">
      <bk-form
        form-type="vertical"
        ref="deptForm"
        :model="deptForm"
        :rules="deptRules">
        <bk-form-item :label="labelMap.deptName" :required="true" property="name">
          <bk-input v-model.trim="deptForm.name" maxlength="120" :placeholder="placeholderMap.deptName"></bk-input>
        </bk-form-item>
        <bk-form-item :label="labelMap.order" property="order">
          <bk-input v-model.number="deptForm.order" type="number" :placeholder="'0'"></bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';

  // Recursive sub-tree component
  const DeptSubTree = {
    name: 'DeptSubTree',
    props: {
      nodes: { type: Array, default: () => [] },
      selectedNode: { type: Object, default: null },
    },
    template: `
      <div>
        <div v-for="node in nodes" :key="node.id" class="dept-tree-node">
          <div
            class="dept-node-content"
            :class="{ 'dept-node-selected': selectedNode && selectedNode.id === node.id }"
            @click="$emit('select', node)">
            <span
              class="bk-icon dept-expand-icon"
              :class="node._expanded ? 'icon-down-shape' : 'icon-right-shape'"
              v-if="node.has_children || (node.children && node.children.length > 0)"
              @click.stop="$emit('toggle', node)">
            </span>
            <span class="dept-expand-placeholder" v-else></span>
            <span class="dept-node-name" :title="node.name">{{ node.name }}</span>
            <span class="dept-node-actions">
              <i class="bk-icon icon-plus" @click.stop="$emit('add', {}, 'new', node)" style="cursor: pointer; font-size: 14px;"></i>
              <i class="bk-icon icon-edit" @click.stop="$emit('edit', node, 'edit', null)" style="cursor: pointer; font-size: 14px; margin-left: 4px;"></i>
            </span>
          </div>
          <div v-if="node._expanded && node.children && node.children.length > 0" style="padding-left: 20px;">
            <dept-sub-tree
              :nodes="node.children"
              :selected-node="selectedNode"
              @select="$emit('select', $event)"
              @toggle="$emit('toggle', $event)"
              @add="$emit('add', $event)"
              @edit="$emit('edit', $event)">
            </dept-sub-tree>
          </div>
        </div>
      </div>
    `,
  };

  export default {
    name: 'DepartmentManagement',
    components: { DeptSubTree },
    data() {
      return {
        secondClick: false,
        treeLoading: false,
        treeData: [],
        selectedNode: null,
        // 成员
        memberLoading: false,
        memberList: [],
        memberPagination: { current: 1, count: 0, limit: 10 },
        // Dialog
        deptDialog: { isShow: false, mode: 'new', parentNode: null },
        deptForm: { name: '', order: 0, parent: null },
        deptRules: {
          name: [{ required: true, message: this.placeholderMap.deptName, trigger: 'blur' }],
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      labelMap() {
        const t = this.$t.bind(this);
        return {
          chname: t('m.userManagement["中文名"]'),
          username: t('m.userManagement["用户名"]'),
          isPrimary: t('m.userManagement["是否主部门"]'),
          deptName: t('m.userManagement["部门名称"]'),
          order: t('m.userManagement["排序"]'),
        };
      },
      placeholderMap() {
        const t = this.$t.bind(this);
        return {
          deptName: t('m.userManagement["请输入部门名称"]'),
        };
      },
      dialogTitleNew() {
        return this.$t('m.userManagement["新建部门"]');
      },
      dialogTitleEdit() {
        return this.$t('m.userManagement["编辑部门"]');
      },
    },
    mounted() {
      this.loadRootDepts();
    },
    methods: {
      // --- 树操作 ---
      loadRootDepts() {
        this.treeLoading = true;
        this.$store.dispatch('department/tree', { parent__isnull: true }).then((res) => {
          this.treeData = (res.data.results || res.data).map(n => ({ ...n, _expanded: false, children: [] }));
        })
          .catch((res) => { errorHandler(res, this); })
          .finally(() => { this.treeLoading = false; });
      },
      toggleNode(node) {
        if (node._expanded) {
          node._expanded = false;
          return;
        }
        // 懒加载子部门
        if (!node.children || node.children.length === 0) {
          this.$store.dispatch('department/tree', { parent: node.id }).then((res) => {
            node.children = (res.data.results || res.data).map(n => ({ ...n, _expanded: false, children: [] }));
            node._expanded = true;
          })
            .catch((res) => { errorHandler(res, this); });
        } else {
          node._expanded = true;
        }
      },
      selectNode(node) {
        this.selectedNode = node;
        this.memberPagination.current = 1;
        this.loadMembers();
      },
      // --- 成员 ---
      loadMembers() {
        if (!this.selectedNode) return;
        this.memberLoading = true;
        this.$store.dispatch('department/members', {
          id: this.selectedNode.id,
          page: this.memberPagination.current,
          page_size: this.memberPagination.limit,
        }).then((res) => {
          const data = res.data;
          this.memberList = data.results || data;
          this.memberPagination.count = data.count || 0;
        })
          .catch((res) => { errorHandler(res, this); })
          .finally(() => { this.memberLoading = false; });
      },
      onMemberPageChange(page) {
        this.memberPagination.current = page;
        this.loadMembers();
      },
      onMemberPageLimitChange(limit) {
        this.memberPagination.limit = limit;
        this.memberPagination.current = 1;
        this.loadMembers();
      },
      // --- 部门 CRUD ---
      openDeptForm(node, mode, parentNode) {
        this.deptDialog.mode = mode;
        this.deptDialog.parentNode = parentNode;
        this.deptForm = {
          id: node.id || null,
          name: node.name || '',
          order: node.order || 0,
          parent: parentNode ? parentNode.id : (node.parent || null),
        };
        this.deptDialog.isShow = true;
      },
      submitDept() {
        this.$refs.deptForm.validate().then(() => {
          if (this.secondClick) return;
          this.secondClick = true;
          const data = { ...this.deptForm };
          if (!data.parent) delete data.parent;
          const action = this.deptDialog.mode === 'new'
            ? 'department/create'
            : 'department/update';
          this.$store.dispatch(action, data).then(() => {
            this.$bkMessage({
              message: this.deptDialog.mode === 'new'
                ? this.dialogTitleNew + ' ✓'
                : this.dialogTitleEdit + ' ✓',
              theme: 'success',
            });
            this.deptDialog.isShow = false;
            // 刷新树
            this.loadRootDepts();
          })
            .catch((res) => { errorHandler(res, this); })
            .finally(() => { this.secondClick = false; });
        });
      },
    },
  };
</script>

<style scoped>
  .dept-tree-node {
    line-height: 32px;
  }
  .dept-node-content {
    display: flex;
    align-items: center;
    padding: 0 8px;
    border-radius: 2px;
    cursor: pointer;
    position: relative;
  }
  .dept-node-content:hover {
    background-color: #f0f1f5;
  }
  .dept-node-selected {
    background-color: #e1ecff;
  }
  .dept-expand-icon {
    font-size: 12px;
    width: 20px;
    text-align: center;
    cursor: pointer;
    flex-shrink: 0;
  }
  .dept-expand-placeholder {
    width: 20px;
    flex-shrink: 0;
  }
  .dept-node-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .dept-node-actions {
    display: none;
    margin-left: auto;
    flex-shrink: 0;
    gap: 2px;
  }
  .dept-node-content:hover .dept-node-actions {
    display: inline-flex;
  }
</style>
