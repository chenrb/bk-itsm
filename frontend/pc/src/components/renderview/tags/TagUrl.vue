<template>
  <div class="tag-url">
    <template v-if="form.value">
      <span v-if="scheme.isIframe" class="slider-trigger-btn" @click="isSideSliderOpen = true">{{ text }}</span>
      <a v-else class="link" :href="form.value" target="_blank">{{ text }}</a>
    </template>
    <span v-else>{{ form.label || '--' }}</span>
    <bk-sideslider
      v-model:is-show="isSideSliderOpen"
      :quick-close="true"
      :title="text"
      :width="800"
      ext-cls="custom-form-iframe-sideslider">
      <template #content>
        <div class="custom-form-iframe-content">
          <iframe :src="form.value" frameborder="0"></iframe>
        </div>
      </template>
    </bk-sideslider>
  </div>
</template>
<script>
  import { useFormMixins, COMMON_ATTRS } from '@/composables/useFormMixins';

  const textAttrs = {
    styles: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: [String, Array],
      default: '',
    },
  };
  export default {
    name: 'TagUrl',
    setup() {
      return { ...useFormMixins() };
    },
    props: {
      ...COMMON_ATTRS,
      styles: textAttrs.styles,
    },
    data() {
      return {
        isSideSliderOpen: false,
      };
    },
    computed: {
      text() {
        return this.form.label || this.form.value || '--';
      },
    },
  };
</script>
<style lang="scss" scoped>
  .tag-url {
    display: flex;
  }
  .slider-trigger-btn {
    color: #3a84ff;
    cursor: pointer;
  }
  .link {
    color: #3a84ff;
  }
  .custom-form-iframe-content {
    width: 100%;
    height: 100%;
    overflow: hidden;
    iframe {
      width: 100%;
      height: 100%;
    }
  }
</style>
