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

import { ref, getCurrentInstance } from 'vue';

/**
 * Common attributes for form render components.
 * These correspond to the props that form components should accept.
 */
export const COMMON_ATTRS = {
  label: {
    type: String,
    required: false,
  },
  hiddenLabel: {
    type: Boolean,
    default: false,
  },
  form: {
    type: Object,
    default: () => ({}),
  },
  scheme: {
    type: Object,
    default: () => ({}),
  },
  children: {
    type: [String, Array],
    required: false,
  },
  desc: {
    type: String,
    required: false,
  },
};

/**
 * Form mixins composable.
 *
 * Provides form value management and tree traversal utilities for
 * render view form components.
 *
 * Note: The consuming component must handle `inject` for `getContext`
 * using Vue 3's `inject()` function, and `value` should be managed
 * through component props/emit (v-model pattern) or `useAttrs()`.
 *
 * The `getTopViewItem` method uses `getCurrentInstance()` to traverse
 * parent components. It must be called within setup().
 *
 * @param {Object} attrs - Custom attribute definitions for the form component
 * @param {Object} [attrs.value] - Value attribute with a default
 * @returns {Object} Form helpers and state
 */
export function useFormMixins(attrs = {}) {
  const instance = getCurrentInstance();

  // Extract private props (all attrs except 'value')
  const privateProps = {};
  for (const key in attrs) {
    if (key !== 'value') {
      privateProps[key] = attrs[key];
    }
  }

  // Initialize value from $attrs.value or attrs.value.default
  const value = ref(
    instance?.attrs?.value !== undefined
      ? instance.attrs.value
      : (attrs.value && attrs.value.default !== undefined ? attrs.value.default : undefined)
  );

  /**
   * Get the top-level ViewItem component instance by traversing parent components.
   * @returns {Object|null} Top ViewItem component instance
   */
  function getTopViewItem() {
    let vueTag = instance?.proxy;
    let isTop = false;
    while (!isTop) {
      if (vueTag?.$parent && vueTag.$parent.isRootRenderView) {
        isTop = true;
      } else {
        vueTag = vueTag?.$parent;
        if (!vueTag) break;
      }
    }
    return vueTag;
  }

  return {
    value,
    privateProps,
    COMMON_ATTRS,
    getTopViewItem,
  };
}
