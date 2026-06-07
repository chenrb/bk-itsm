import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const SERVER_HOST = env.VITE_SERVER_HOST || 'localhost'
  const SERVER_PORT = parseInt(env.VITE_SERVER_PORT || '8004', 10)
  const API_TARGET = env.VITE_API_TARGET || 'http://localhost:8001'

  return {
    plugins: [
      vue(),
      // 开发模式：使用 index-dev.html 并从 .env 注入 window 全局变量
      {
        name: 'dev-html-inject',
        apply: 'serve',
        configureServer(server) {
          // 将 / 和 /index.html 重写到 index-dev.html
          server.middlewares.use((req, res, next) => {
            if (req.url === '/' || req.url === '/index.html') {
              req.url = '/index-dev.html'
            }
            next()
          })
        },
        transformIndexHtml: {
          enforce: 'pre',
          transform(html) {
            const injectScript = `
    <script>
        // 开发模式配置 — 来自 .env.development
        window.SITE_URL = '/';
        window.STATIC_URL = '/';
        window.VERSION = '${env.VITE_VERSION || 'dev'}';
        window.log_name = '${env.VITE_LOG_NAME || '流程服务'}';
        // 用户数据 — 生产模式由 Django 模板注入
        window.username = '${(env.VITE_USERNAME || '').replace(/'/g, "\\'")}';
        window.chname = '${(env.VITE_CHNAME || '').replace(/'/g, "\\'")}';
        window.IS_ITSM_ADMIN = ${env.VITE_IS_ITSM_ADMIN || '0'};
    </script>`
            return html.replace('<!-- window 全局变量由 vite.config.js 的 dev-html-inject 插件从 .env 注入 -->', injectScript)
          }
        }
      }
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        'vue': 'vue/dist/vue.esm-bundler.js',
        'jquery': 'jquery/dist/jquery.min.js',
        '$': 'jquery/dist/jquery.min.js'
      },
      extensions: ['.js', '.vue', '.json']
    },
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'vuex',
        'axios',
        'lodash',
        'jquery',
        'cookie',
        'js-cookie',
        'jsplumb',
        'moment',
        'dayjs',
        'brace'
      ],
      esbuildOptions: {
        loader: {
          '.svg': 'dataurl',
          '.eot': 'dataurl',
          '.woff': 'dataurl',
          '.ttf': 'dataurl'
        }
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler',
          silenceDeprecations: ['legacy-js-api']
        }
      }
    },
    server: {
      host: SERVER_HOST,
      port: SERVER_PORT,
      https: API_TARGET.startsWith('https'),
      open: false,
      proxy: {
        '/api/': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/openapi/': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/core/': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
      }
    },
    build: {
      outDir: path.resolve(__dirname, '../../../static'),
      assetsDir: 'assets',
      rollupOptions: {
        input: path.resolve(__dirname, 'index.html'),
        output: {
          chunkFileNames: 'assets/js/[name].[hash].js',
          entryFileNames: 'assets/js/[name].[hash].js',
          assetFileNames: 'assets/[ext]/[name].[hash].[ext]'
        }
      }
    }
  }
})
