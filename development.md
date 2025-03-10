# vue-fastapi-admin 模板使用

## 1. 后端目录解析
- `app/models`: 主要是定义数据库模型
- `app/schemas`: 主要是定义数据库之外的一些模型，例如对应API请求数据时，用一个账号密码模型等
- `app/controllers`: 控制器，定义一些模型对应的操作，如用户的CRUD、API的刷新之类的
  - `app/core`: 核心功能，全局的CRUD、后台任务、上下文、初始化等的管理，异步编程中的上下文管理使用了`contextvars`

## 2. 要添加模块
- **后端**
  1. 增加对应的数据库数据，`app/models/admin.py`下新增数据库类，这里使用了`tortoise`进行数据库操作(没使用到可以不加)
  2. 在`app/schemas/`下新增对应的数据（结构模型）验证文件，这里使用了`Pydantic`进行定义数据模型，并使用这些模型对数据进行验证和转换。(无特定数据校验可以不用)
  3. 在`app/controllers/`下增加模块操作文件，主要是供API中调用(主要逻辑,比如爬虫代码什么的,供调用)
  4. 注册路由，`app/api/v1/`下新增API文件夹及对应文件，并相应修改`app/api/v1/__init__.py`，这里使用了`fastapi` (其中`app/api/__init__.py`也一起改,内容在对应代码文件中都有,可以参考)

- **前端**
  1. 在`web/src/api/index.js`中增加API的接口定义
  2. 在`web/src/routes/index.js`中新增页面路由
  3. 在`web/src/views`中合适位置新增页面即可

## 3. 运行
- **后端**
  - 模板依赖Python 3.11
  - 安装虚拟环境（项目根目录执行）：`python -m venv venv`
  - 激活虚拟环境：
    - Windows: `venv\Scripts\activate`
    - Mac: `source venv/bin/activate`
  - 使用Anaconda也可以,直接Anaconda Navigator安装Python3.11和nodejs 20(node版本要求>18.8.0)
  - 安装库：
    - 先注释掉`requirements.txt`中的`uvloop`  这个库在windows里没有
    - `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
  - 启动服务：`python run.py`，服务现在应该正在运行，访问`http://localhost:9999/docs` 查看API文档

- **前端**
  - 进入前端目录 `cd web`
  - 安装依赖（建议使用pnpm）：`pnpm i` 或者 `npm i`
    - 如果网络不通可以先换源：
      ```bash
      pnpm config set registry https://registry.npmmirror.com
      # 还原:
      pnpm config set registry https://registry.npmjs.org
      # 查看当前使用的源:
      pnpm get registry
      ```
  - 启动（在web目录下）：访问 `http://localhost:3100/` 即可查看网页

- **后续二次启动**:
选择好解释器(Conda / .venv )
- 终端1
  ```
  python run.py
  ```
- 终端2
  ```
  cd web
  ```
  ```
  pnpm dev
  ```

- **注意!**：在`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` 需要先注释掉`requirements.txt`中的`uvloop`，这个库不支持Windows，主要用于优化协程的事件循环，不安装也不影响运行
- 模板的创建API功能和创建菜单是能创建对应视图，但是因为没有路由和控制器，是没有用的;只当是个样式模板。


---
---

# 具体操作示例Demo:以这个实际为准
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

2. 在`web/src/views`中合适位置新增页面,点击对应栏目就可以展示vue界面了
      创建文件夹,里面放一个vue文件
      ```
      views
        └─ xxx (父模块目录 文件夹)    
             └─ xxx (子模块菜单  文件夹)    
                 └─index.vue   (网页界面文件) 
      ```


3. 在`web/src/api/index.js`中增加api的接口定义
    该文件的其他代码如何定义接口作为参考;
    ```
    export default {
    ...
       fetchDocumentData: () => request.get('/document/fetch'),
    ...
    }
    ```
    
    
    

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
    
  - #app/api/v1/document/__init__.py

    ```
    from fastapi import APIRouter
    from .document import router

    document_router = APIRouter()
    #document_router.include_router(router, prefix="/document", tags=["测试"])
    document_router.include_router(router, tags=["测试"])
    #此处内容在 系统管理/API管理  点击刷新后  会更新到页面上

    __all__ = ["document_router"]
    ```

    
  - #app/api/v1/document/document.py
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

  - 然后在上一级文件夹中的`__init__.py`中加入刚才配置的路由:
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

# 具体操作示例Demo:以这个示例为准
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

2. 在`web/src/views`中合适位置新增页面,点击对应栏目就可以展示vue界面了
      创建文件夹,里面放一个vue文件
<br/>

3. 在`web/src/api/index.js`中增加api的接口定义
    该文件的其他代码如何定义接口作为参考;

    ```
    fetchDocumentData: () => request.get('/document/fetch'),
    ```

- **后端**
1. 在`app/controllers/`下增加模块操作文件，主要是供api中调用

    ```
    # document.py
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
    ```
    #app/api/v1/document/__init__.py
    from fastapi import APIRouter
    from .document import router

    document_router = APIRouter()
    #document_router.include_router(router, prefix="/document", tags=["测试"])
    document_router.include_router(router, tags=["测试"])
    #此处内容在 系统管理/API管理  点击刷新后  会更新到页面上

    __all__ = ["document_router"]
    ```

    ```
    #app/api/v1/document/document.py
    from fastapi import APIRouter
    from app.controllers.document import document_controller
    from app.schemas import Success

    router = APIRouter()

    @router.get("/fetch", summary="获取爬虫数据")
    async def fetch_document_data():
        data =  await document_controller.fetch_data()
        return Success(data = data) 
    ```

3. 在`app/core/init_app.py`中增加初始化操作 (非必要操作,暂时不用)