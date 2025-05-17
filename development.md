# vue-fastapi-admin 模板使用


# 要添加模块：
- **后端**
  1. 增加对应的数据库数据，`app/models/admin.py`下新增数据库类，这里使用了`tortoise`进行数据库操作(没使用到可以不加)
  2. 在`app/schemas/`下新增对应的数据（结构模型）验证文件，这里使用了`Pydantic`进行定义数据模型，并使用这些模型对数据进行验证和转换。(无特定数据校验可以不用)
  3. 在`app/controllers/`下增加模块操作文件，主要是供API中调用(主要逻辑,比如爬虫代码什么的,供调用)
  4. 注册路由，`app/api/v1/`下新增API文件夹及对应文件，并相应修改`app/api/v1/__init__.py`，这里使用了`fastapi` (其中`app/api/__init__.py`也一起改,内容在对应代码文件中都有,可以参考)

- **前端**
  1. 在`web/src/api/index.js`中增加API的接口定义
  2. 在`web/src/routes/index.js`中新增页面路由
  3. 在`web/src/views`中合适位置新增页面即可


# 具体操作示例Demo:以这个实际为准
- **后端**
1. 在`app/controllers/`下增加模块操作文件，主要是供api中调用;这里以爬取`tiobe`网站上最受欢迎的编程语言的前`10`在页面上进行浏览;

  - document.py
    ```
    import requests
    from bs4 import BeautifulSoup

    class DocumentController:
        @staticmethod
        async def fetch_data():
            res = requests.get("https://www.tiobe.com/tiobe-index/")
            if res.status_code == 200:
                sp = BeautifulSoup(res.text, 'html.parser')
                best = sp.select('tbody tr td:nth-child(5)')
                if len(best) != 0:
                    result = "TIOBE目前排名前10的编程语言是：\n" + "\n".join(
                        [f"Top {i+1}: {best[i].getText()}" for i in range(10)]
                    )
                    return result
            return result(content="获取数据失败")

    document_controller = DocumentController()
    ```

2. 注册路由，`app/api/v1/`下新增api文件夹及对应文件(比如xxx模块,就建立xxx文件夹,里面放xxx.py和__init__.py)，并相应修改`app/api/v1/__init__.py`注册路由，这里使用了fastapi
  - # 修改文件1：
  - ## app/api/v1/document/__init__.py

    ```
    from fastapi import APIRouter
    from .document import router

    document_router = APIRouter()
    #document_router.include_router(router, prefix="/document", tags=["测试"])
    document_router.include_router(router, tags=["测试"])
    #此处内容在 系统管理/API管理  点击刷新后  会更新到页面上

    __all__ = ["document_router"]
    ```

  - # 修改文件2：
  - ## app/api/v1/document/document.py 
    ```
    from fastapi import APIRouter
    from app.controllers.document import document_controller
    from app.schemas import Success

    router = APIRouter()

    @router.get("/fetch", summary="获取爬虫数据")
    async def fetch_document_data():
        data =  await document_controller.fetch_data()
        return Success(data = data) 
    ```

  - 然后在上一级文件夹中的`__init__.py`，即`app/api/v1/__init__.py`中加入刚才配置的路由:
  - # 修改文件3：
  - ## app/api/v1/__init__.py
    ```
    from fastapi import APIRouter
    from app.core.dependency import DependPermisson

    from .document import document_router #demo

    v1_router = APIRouter()
    v1_router.include_router(document_router, prefix="/document", dependencies=[DependPermisson]) #demo
    ```

  - # 修改文件4：
  - ## app/api/__init__.py
    ```
    from fastapi import APIRouter
    from .v1 import v1_router
    
    from .v1.document import document_router  # 新增

    api_router = APIRouter()
    api_router.include_router(v1_router, prefix="/v1")

    api_router.include_router(document_router, prefix="/v1") #新增


    __all__ = ["api_router"]
    ```


3. 在`app/core/init_app.py`中增加初始化操作 (非必要操作,暂时不用)





- **前端**

1. 到`web/src/router/routes/index.js`中增加侧边栏的定义代码片段,举个例子:在export const basicRoutes 下找到合适的位置(我已经给出例子),增加对应的子目录和子菜单栏
      ```
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
      ```

2. 在`web/src/api/index.js`中增加api的接口定义
    该文件的其他代码如何定义接口作为参考;
    ```
    export default {
    ...
       fetchDocumentData: () => request.get('/document/fetch'),
    ...
    }
    ```


3. 在`web/src/views`中合适位置新增页面,点击对应栏目就可以展示vue界面了
      创建文件夹,里面放一个vue文件
      ```
      views
        └─ xxx (父模块目录 文件夹)    
             └─ xxx (子模块菜单  文件夹)    
                 └─index.vue   (网页界面文件) 
      ```
      我的`web\src\views\data-collection\document\index.vue`内容如下：
      ```
      <template>
        <div>
          <button @click="fetchData">获取 TIOBE 排名前10编程语言</button>
          <div v-if="content">
            <h3>爬虫结果：</h3>
            <pre>{{ content }}</pre>
          </div>
        </div>
      </template>

      <script>
      import api from '@/api'

      export default {
        data() {
          return {
            content: null,
          }
        },

        methods: {
          async fetchData() {
            try {
              const response = await api.fetchDocumentData()
              this.content = response.data
            } catch (error) {
              console.error('获取数据失败', error)
            }
          },
        },
      }
      </script>

      ```