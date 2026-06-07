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

import "./globals";
import { createApp } from "vue";
import { createPinia } from "pinia";
import cookie from "cookie";
import $ from "jquery";
import * as monaco from "monaco-editor";
// bkui-vue (BlueKing Vue 3 component library)
import bkui, { clickoutside, bkTooltips } from "bkui-vue";
import "bkui-vue/dist/style.css";
import VueDOMPurifyHTML from 'vue-dompurify-html';
// view components
import App from "./App";
// components
import router from "./router";
import Exception from "./components/common/exception";
import ArrowsLeftIcon from "./components/common/layout/ArrowsLeftIcon";
import i18n from "./i18n/index.js";
import store from "./store";
// 自定义指令
import directives from "./directives";
import { cursor } from "./directives/cursor.js";
import ace from "brace";
import { renderHeader } from './utils/util';
import "brace/mode/javascript";
import "brace/mode/python";
import "brace/mode/json";
import "brace/mode/yaml";
import "brace/theme/monokai";
import "brace/theme/textmate";
import "brace/theme/solarized_dark";

window.$ = $;
window.monaco = monaco;

const app = createApp(App);

// 注册插件
const pinia = createPinia();
app.use(pinia);
app.use(store);
app.use(router);
app.use(i18n);
app.use(bkui);
app.use(VueDOMPurifyHTML);

// 注册自定义指令
app.directive('clickoutside', clickoutside);
app.directive('bk-clickoutside', clickoutside);
app.directive('bk-tooltips', bkTooltips);
app.directive('bk-overflow-tips', bkTooltips);
app.directive('clickOut', directives.clickOut);
app.directive('focus', directives.focus);
app.directive('anchor', directives.anchor);
app.directive('cursorIndex', directives.cursorIndex);
app.directive('bk-focus', directives.bkFocus);
app.directive('cursor', cursor);
app.directive('permission', directives.permission);

// 全局属性
app.config.globalProperties.$ace = ace;
app.config.globalProperties.$cookie = cookie;
app.config.globalProperties.$renderHeader = renderHeader;

// renderForm 来自外部脚本 /js/renderform/index.js
if (typeof renderForm !== 'undefined') {
  app.use(renderForm);
}

// 全局组件
app.component("app-exception", Exception);
app.component("arrows-left-icon", ArrowsLeftIcon);

// 国际化
const localeCookie = cookie.parse(document.cookie).itsm_language || "zh-cn";

store.commit("setLanguage", localeCookie);

function mountApp() {
  try {
    app.mount("#app");
    window.app = app;
  } catch (e) {
    console.error('[ITSM] mount error:', e);
  }
}

store.dispatch('getPlatformPreData').then((data) => {
  console.log('[ITSM] init done, username:', window.username, 'data:', data);
  store.dispatch('user/syncPermissions');
  mountApp();
}).catch((err) => {
  console.error('[ITSM] init FAILED, err:', err, 'username:', window.username);
  // session 无效时仍然 mount，让路由守卫重定向到登录页
  mountApp();
});



