import './cursor.js';
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

export default {
  clickOut,
  focus,
  anchor,
  cursorIndex,
  bkFocus,
};
