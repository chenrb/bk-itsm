import { createApp, h } from 'vue';
import SidesliderVue from './Sideslider.vue';

const Sideslider = (options = {
  title: 'title',
  formData: [],
  context: {
    schemes: {},
  },
}) => {
  const container = document.createElement('div');
  document.body.appendChild(container);

  const app = createApp({
    render() {
      return h(SidesliderVue, {
        isShow: true,
        title: options.title,
        formData: options.formData,
        context: options.context,
        'onUpdate:isShow': (show) => {
          if (!show) {
            app.unmount();
            container.remove();
          }
        }
      });
    }
  });

  app.mount(container);
  return app;
};

export default Sideslider;
