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
      vue()
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
        '/api/*': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/init': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/openapi/*': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/core/': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/o/bk_sops/*': {
          target: API_TARGET,
          changeOrigin: true,
          secure: false,
        },
        '/sops/*': {
          target: API_TARGET.replace(/\/$/, '') + '/o/bk_sops/',
          changeOrigin: true,
          secure: false,
        }
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
