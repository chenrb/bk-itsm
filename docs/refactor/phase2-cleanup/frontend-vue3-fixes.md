# P2-18: 前端 Vue 3 编译与运行时错误修复

完成 Phase 1 重构后，前端 dev server 启动后大量页面编译失败、运行时崩溃。本阶段系统性修复 Vue 3 兼容性问题和模板语法错误，使前端可以正常启动并访问所有页面。

## 修复分类

### 1. 依赖缺失

- `package.json` 添加 `less` 开发依赖（`bkui-vue` 使用 `.less` 文件）
- 复制 `static/js/renderform/` → `frontend/pc/public/js/renderform/`（`index.html` 引用了 `/js/renderform/index.js`，Vite dev server 不服务 Django static 目录）

### 2. SCSS 路径

- `src/scss/bk-new-change.scss`：`./scss/mixins/scroller.scss` → `./mixins/scroller.scss`（路径多了一层 `scss/`）
- 全局替换 `~@/` → `@/`（Vite 原生支持 `@` 别名，不需要 webpack 的 `~` 前缀），涉及 20 处

### 3. `<template #slotName>` 未闭合标签（约 90 个文件）

旧代码中 `<template #slotName><div>` 写在同一行且缺少 `</template>` 闭合。修复方式：拆分为独立行并补上闭合标签。涉及 `#header`、`#footer`、`#content`、`#empty`、`#extension`、`#dropdown-trigger`、`#dropdown-content`、`#append`、`#prepend` 等插槽。

### 4. `<template v-for>` 的 `:key` 放置（33 个文件）

Vue 3 要求 `:key` 放在 `<template>` 上，不能放在子元素上：

```html
<!-- 错误 -->
<template v-for="item in list">
  <div :key="item.id">{{ item.name }}</div>
</template>

<!-- 正确 -->
<template v-for="item in list" :key="item.id">
  <div>{{ item.name }}</div>
</template>
```

### 5. `<template #slotName>` 错位（5 个文件）

- `addApiInfo.vue`：`<template #prepend>` 空 wrapper 包裹 `<template #append>` — 删除空的 `#prepend`
- `eventRemind.vue`：`<template #append>` 放在 `<span>` 内 — 命名插槽只能在组件的直接子级，删除 `#append` 包装

### 6. 导入路径错误（3 个文件）

- `personSelect.vue`、`taskLibrary.vue`：3 个 import 路径少了一层 `../`
- `taskLog.vue`：`import slaRecord from './slaRecord'` 指向不存在的文件，改为 `'../rightTicketTabs/SlaRecordTab.vue'`

### 7. Vue 2 遗留代码

- `router/index.js`：移除 `Vue.use(Router)`（Vue 3 通过 `app.use(router)` 注册）
- `store/modules/change.js`：移除未使用的 `import { i18n } from "../../main"`

### 8. vue-i18n v9 API 兼容（30 个文件）

vue-i18n v9 在 `legacy: true` 模式下翻译函数是 `i18n.global.t()` 不是 `i18n.t()`。每个文件添加：

```js
const t = i18n.global.t.bind(i18n.global);
```

然后将所有 `i18n.t(` 替换为 `t(`。涉及 `routerList.js`、`useTicketListMixins.js`、`constants/task.js`、`constants/ticket.js`、`store/index.js`、`stores/root.js`、`utils/util.js` 和 23 个 Vue 组件。

### 9. mitt 事件总线 API（8 个文件）

`bus.js` 使用 `mitt`，但消费方仍使用 Vue 2 的 `bus.$on/$emit/$off`。全部替换为 mitt 的 `bus.on/emit/off`：

- `App.vue`、`Navigation.vue`、`usePermission.js`、`router/index.js`、`ajax.js`、`serviceList.vue`、`guide.vue`、`ticket/details/index.vue`

## 验证结果

- `npm run dev` 启动成功（Vite 4.5 + 端口 8004）
- 全量扫描 **295 个 `.vue` 文件**通过编译（HTTP 200），0 失败
- 主页面可正常加载，路由跳转无白屏

## 影响范围

约 **150 个前端文件**修改，主要在 `frontend/pc/src/` 下：
- 90 个 `.vue` 文件：模板标签闭合 + `:key` 位置
- 30 个 `.vue/.js` 文件：`i18n.t` → `t` 替换
- 8 个文件：`bus.$on/emit/off` → `bus.on/emit/off`
- 1 个 `package.json`、1 个 SCSS 文件
- 新增 `frontend/pc/public/js/renderform/` 目录

## 经验教训

迁移 Vue 2 → Vue 3 时，以下问题需重点关注：

1. **`<template v-for>` 的 `:key`**：必须放在 `<template>` 上
2. **命名插槽 `<template #slot>`**：必须有闭合标签，且只能在组件的直接子级
3. **vue-i18n v9**：`legacy` 模式下用 `i18n.global.t`，composition 模式下用 `useI18n()`
4. **事件总线**：Vue 3 移除了实例上的 `$on/$emit/$off`，需用 `mitt` 等独立库
5. **Vite 与 webpack**：`~@/` 别名前缀是 webpack 专属，Vite 直接用 `@/`
