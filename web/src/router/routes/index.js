import i18n from '~/i18n'
const { t } = i18n.global

const Layout = () => import('@/layout/index.vue')

export const basicRoutes = [
  {
    path: '/',
    redirect: '/workbench', // 默认跳转到首页
    meta: { order: 0 },
  },
  {
    name: t('views.workbench.label_workbench'),
    path: '/workbench',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/workbench/index.vue'),
        name: `${t('views.workbench.label_workbench')}Default`,
        meta: {
          title: t('views.workbench.label_workbench'),
          icon: 'icon-park-outline:workbench',
          affix: true,
        },
      },
    ],
    meta: { order: 1 },
  },
  {
    name: t('views.profile.label_profile'),
    path: '/profile',
    component: Layout,
    isHidden: true,
    children: [
      {
        path: '',
        component: () => import('@/views/profile/index.vue'),
        name: `${t('views.profile.label_profile')}Default`,
        meta: {
          title: t('views.profile.label_profile'),
          icon: 'user',
          affix: true,
        },
      },
    ],
    meta: { order: 99 },
  },
  {
    name: 'ErrorPage',
    path: '/error-page',
    component: Layout,
    redirect: '/error-page/404',
    meta: {
      title: t('views.errors.label_error'),
      icon: 'mdi:alert-circle-outline',
      order: 99,
    },
    children: [
      {
        name: 'ERROR-401',
        path: '401',
        component: () => import('@/views/error-page/401.vue'),
        meta: {
          title: '401',
          icon: 'material-symbols:authenticator',
        },
      },
      {
        name: 'ERROR-403',
        path: '403',
        component: () => import('@/views/error-page/403.vue'),
        meta: {
          title: '403',
          icon: 'solar:forbidden-circle-line-duotone',
        },
      },
      {
        name: 'ERROR-404',
        path: '404',
        component: () => import('@/views/error-page/404.vue'),
        meta: {
          title: '404',
          icon: 'tabler:error-404',
        },
      },
      {
        name: 'ERROR-500',
        path: '500',
        component: () => import('@/views/error-page/500.vue'),
        meta: {
          title: '500',
          icon: 'clarity:rack-server-outline-alerted',
        },
      },
    ],
  },


  //侧边栏增加自己想要的页面操作
  ///////////////////START///////////////////////////////
  {
    name: t('数据收集'), 
    path: '/data-collection',
    component: Layout,
    meta: {
      title: t('数据收集'),
      icon: 'material-symbols:database',
      order: 10,
    },
    children: [
      {
        name: '论文收集',
        path: 'paper',
        component: () => import('@/views/data-collection/paper/index.vue'),  //自己创建;
        meta: {
          title: '论文收集',
          icon: 'material-symbols:edit-document',
        },
      },
      {
        name: '专利收集',
        path: 'patent',
        component: () => import('@/views/data-collection/patent/index.vue'),  //自己创建;
        meta: {
          title: '专利收集',
          icon: 'material-symbols:book-4-rounded',
        },
      },
      {
        name: '文档收集',
        path: 'document',
        component: () => import('@/views/data-collection/document/index.vue'),  //自己创建;
        meta: {
          title: '文档收集',
          icon: 'material-symbols:lab-profile',
        },
      },
      {
        name: '社交媒体收集',
        path: 'social-media',
        component: () => import('@/views//data-collection/social-media/index.vue'), //
        meta: {
          title: '社交媒体收集',
          icon: 'mdi:play-network',
        },
      },
    ],
  },
  ///////////////////////////数据库栏目////////////////////////////////////
  {
    name: t('数据库'), 
    path: '/database',
    component: Layout,
    meta: {
      title: t('数据库'),
      icon: 'material-symbols-light:data-table-outline',
      order: 11,
    },
    children: [
      {
        name: '论文库',
        path: 'papers',
        component: () => import('@/views/database/papers/index.vue'),  //自己创建;
        meta: {
          title: '论文库',
          icon: 'material-symbols:edit-document',
        },
      },
      {
        name: '专利库',
        path: 'patents',
        component: () => import('@/views/database/patents/index.vue'),  //自己创建;
        meta: {
          title: '专利库',
          icon: 'material-symbols:book-4-rounded',
        },
      },
      {
        name: '文档库',
        path: 'documents',
        component: () => import('@/views/database/documents/index.vue'),  //自己创建;
        meta: {
          title: '文档库',
          icon: 'material-symbols:lab-profile',
        },
      },
      {
        name: '社交媒体库',
        path: 'social-medias',
        component: () => import('@/views//database/social-medias/index.vue'), //
        meta: {
          title: '社交媒体库',
          icon: 'mdi:play-network',
        },
      },
    ],
  },
  //////////////////////END//////////////////////////////



  {
    name: '403',
    path: '/403',
    component: () => import('@/views/error-page/403.vue'),
    isHidden: true,
  },
  {
    name: '404',
    path: '/404',
    component: () => import('@/views/error-page/404.vue'),
    isHidden: true,
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    isHidden: true,
    meta: {
      title: '登录页',
    },
  },
]

export const NOT_FOUND_ROUTE = {
  name: 'NotFound',
  path: '/:pathMatch(.*)*',
  redirect: '/404',
  isHidden: true,
}

export const EMPTY_ROUTE = {
  name: 'Empty',
  path: '/:pathMatch(.*)*',
  component: null,
}

const modules = import.meta.glob('@/views/**/route.js', { eager: true })
const asyncRoutes = []
Object.keys(modules).forEach((key) => {
  asyncRoutes.push(modules[key].default)
})

// 加载 views 下每个模块的 index.vue 文件
const vueModules = import.meta.glob('@/views/**/index.vue')

export { asyncRoutes, vueModules }
