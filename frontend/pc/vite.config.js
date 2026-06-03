import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const HOST = env.VITE_DEV_HOST || 'localhost'
  const ORIGIN = `http://${HOST}:${env.VITE_DEV_PORT || '8000'}`
  const SET_URL = env.VITE_SET_URL || ''

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
      host: HOST ? `dev.${HOST}` : 'localhost',
      port: 8004,
      https: ORIGIN.indexOf('https') > -1,
      open: false,
      proxy: {
        '/api/*': {
          target: ORIGIN + SET_URL,
          changeOrigin: true,
          secure: false,
          headers: {
            referer: ORIGIN
          }
        },
        '/init': {
          target: ORIGIN + SET_URL,
          changeOrigin: true,
          secure: false,
          headers: {
            referer: ORIGIN
          }
        },
        '/openapi/*': {
          target: ORIGIN + SET_URL,
          changeOrigin: true,
          secure: false,
          headers: {
            referer: ORIGIN
          }
        },
        '/core/': {
          target: ORIGIN + SET_URL,
          changeOrigin: true,
          secure: false,
          headers: {
            referer: ORIGIN
          }
        },
        '/o/bk_sops/*': {
          target: ORIGIN,
          changeOrigin: true,
          secure: false,
          headers: {
            referer: ORIGIN
          }
        },
        '/sops/*': {
          target: ORIGIN + '/o/bk_sops/',
          changeOrigin: true,
          secure: false
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
