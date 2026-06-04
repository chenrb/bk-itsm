import './cursor.js';
import store from '@/store';
// Vue 3 directive hooks: created, beforeMount, mounted, beforeUpdate, updated,
// beforeUnmount, unmounted. The compat layer maps bind→beforeMount, inserted→mounted,
// update→updated, componentUpdated→updated, unbind→beforeUnmount.

const clickOut = {
  async bind(el, binding) {
    let cascaderFunction = '';
    const documentHandler = await async function (e) {
      if (!el.contains(e.target)) {
        if (!cascaderFunction) {
          cascaderFunction = binding.value;
        } else {
          await binding.value();
          await document.removeEventListener('click', documentHandler);
        }
      }
    };
    await document.addEventListener('click', documentHandler);
  },
  inserted() {
  },
  async update(el, binding) {
    let cascaderFunction = '';
    const documentHandler = await async function (e) {
      if (!el.contains(e.target)) {
        if (!cascaderFunction) {
          cascaderFunction = binding.value;
        } else {
          await binding.value();
          await document.removeEventListener('click', documentHandler);
        }
      }
    };
    await document.addEventListener('click', documentHandler);
  },
};

const focus = {
  update(el, { value }) {
    if (value) {
      el.focus();
    }
  },
};

const anchor = {
  bind(el, binding) {
    binding.value.el = el;
  },
  update() {
  },
  componentUpdated() {
  },
};

const cursorIndex = {
  bind: (el, binding) => {
    const dom = el.querySelector('textarea,input');
    if (dom) {
      const handlerFocus = () => {
        sessionStorage.removeItem('cursorIndex');
      };
      const handlerBlur = (e) => {
        const recordJson = {
          name: binding.value,
          start: e.target.selectionStart,
          end: e.target.selectionEnd,
        };
        sessionStorage.setItem('cursorIndex', JSON.stringify(recordJson));
      };
      dom.addEventListener('focus', handlerFocus, false);
      dom.addEventListener('blur', handlerBlur, false);
    }
  },
};

const bkFocus = {
  inserted(el) {
    const dom = el.querySelector('textarea,input');
    if (['textarea', 'input'].includes(el.tagName)) {
      el.focus();
    } else if (dom) {
      dom.focus();
    }
  },
};

/**
 * v-permission directive: show/hide element based on permission code.
 * Usage: v-permission="'feature:system:user-manage'"
 * Superuser (IS_ITSM_ADMIN === 1) always sees the element.
 */
const permission = {
  mounted(el, binding) {
    const code = binding.value;
    if (!code) return;
    if (window.IS_ITSM_ADMIN === 1) return;
    const permissions = store.state.user?.permissions || [];
    if (!permissions.includes(code)) {
      el.style.display = 'none';
    }
  },
  updated(el, binding) {
    const code = binding.value;
    if (!code) {
      el.style.display = '';
      return;
    }
    if (window.IS_ITSM_ADMIN === 1) {
      el.style.display = '';
      return;
    }
    const permissions = store.state.user?.permissions || [];
    el.style.display = permissions.includes(code) ? '' : 'none';
  },
};

export default {
  clickOut,
  focus,
  anchor,
  cursorIndex,
  bkFocus,
  permission,
};
