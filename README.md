<h1 align="center">InnovTrace</h1>

##### 访问

http://localhost:9999

username：admin

password：123456

### 本地启动
#### 后端
启动项目需要以下环境：
- Python 3.11

#### Pip 安装依赖
1. 创建虚拟环境 Conda也行
```sh
python3.11 -m venv venv
```
2. 激活虚拟环境
```sh
source venv/bin/activate
```
3. 安装依赖
```sh
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
3. 启动服务
```sh
python run.py
```

服务现在应该正在运行，访问 http://localhost:9999/docs 查看API文档

#### 前端
启动项目需要以下环境：
- node v18.8.0+

1. 进入前端目录
```sh
cd web
```

2. 安装依赖(建议使用pnpm: https://pnpm.io/zh/installation)
```sh
npm i -g pnpm # 已安装可忽略
pnpm i # 或者 npm i
```

3. 启动
```sh
pnpm dev
```

### 目录说明
- 仅供参考,`web`目录没标出
```
├── app                   // 应用程序目录
│   ├── api               // API接口目录
│   │   └── v1            // 版本1的API接口
│   │       ├── apis      // API相关接口
│   │       ├── base      // 基础信息接口
│   │       ├── menus     // 菜单相关接口
│   │       ├── roles     // 角色相关接口
│   │       └── users     // 用户相关接口
│   ├── controllers       // 控制器目录
│   ├── core              // 核心功能模块
│   ├── log               // 日志目录
│   ├── models            // 数据模型目录
│   ├── schemas           // 数据模式/结构定义
│   ├── settings          // 配置设置目录
│   └── utils             // 工具类目录
├── deploy                // 部署相关目录
│   └── sample-picture    // 示例图片目录
└── web                   // 前端网页目录
    ├── build             // 构建脚本和配置目录
    │   ├── config        // 构建配置
    │   ├── plugin        // 构建插件
    │   └── script        // 构建脚本
    ├── public            // 公共资源目录
    │   └── resource      // 公共资源文件
    ├── settings          // 前端项目配置
    └── src               // 源代码目录
        ├── api           // API接口定义
        ├── assets        // 静态资源目录
        │   ├── images    // 图片资源
        │   ├── js        // JavaScript文件
        │   └── svg       // SVG矢量图文件
        ├── components    // 组件目录
        │   ├── common    // 通用组件
        │   ├── icon      // 图标组件
        │   ├── page      // 页面组件
        │   ├── query-bar // 查询栏组件
        │   └── table     // 表格组件
        ├── composables   // 可组合式功能块
        ├── directives    // 指令目录
        ├── layout        // 布局目录
        │   └── components // 布局组件
        ├── router        // 路由目录
        │   ├── guard     // 路由守卫
        │   └── routes    // 路由定义
        ├── store         // 状态管理(pinia)
        │   └── modules   // 状态模块
        ├── styles        // 样式文件目录
        ├── utils         // 工具类目录
        │   ├── auth      // 认证相关工具
        │   ├── common    // 通用工具
        │   ├── http      // 封装axios
        │   └── storage   // 封装localStorage和sessionStorage
        └── views         // 视图/页面目录
            ├── error-page // 错误页面
            ├── login      // 登录页面
            ├── profile    // 个人资料页面
            ├── system     // 系统管理页面
            └── workbench  // 工作台页面
```
---
---
---
---
---

# vue-fastapi-admin 模板使用

## 1. 后端目录解析
- `app/models`: 主要是定义数据库模型
- `app/schemas`: 主要是定义数据库之外的一些模型，例如对应API请求数据时，用一个账号密码模型等
- `app/controllers`: 控制器，定义一些模型对应的操作，如用户的CRUD、API的刷新之类的
  - `app/core`: 核心功能，全局的CRUD、后台任务、上下文、初始化等的管理，异步编程中的上下文管理使用了`contextvars`

## 2. 要添加模块
- **后端**
  1. 增加对应的数据库数据，`app/models/admin.py`下新增数据库类，这里使用了`tortoise`进行数据库操作
  2. 在`app/schemas/`下新增对应的数据（结构模型）验证文件，这里使用了`Pydantic`进行定义数据模型，并使用这些模型对数据进行验证和转换。
  3. 在`app/controllers/`下增加模块操作文件，主要是供API中调用
  4. 注册路由，`app/api/v1/`下新增API文件夹及对应文件，并相应修改`app/api/v1/__init__.py`，这里使用了`fastapi`
  5. 在`app/core/init_app.py`中增加初始化操作

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

- **注意!!!!!!!!!!!!!!!!!!!!**：在`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` 需要先注释掉`requirements.txt`中的`uvloop`，这个库不支持Windows，主要用于优化协程的事件循环，不安装也不影响运行
- 模板的创建API功能和创建菜单是能创建，但是因为没有路由和控制器，是没有用的;只当是个样式模板。


---
---
---
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
        


3. 在`web/src/api/index.js`中增加api的接口定义
    该文件的其他代码如何定义接口作为参考;

    ```
    fetchDocumentData: () => request.get('/document/fetch'),
    ```

- **后端**
1. 在`app/controllers/`下增加模块操作文件，主要是供api中调用

  
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

3. 在`app/core/init_app.py`中增加初始化操作 (非必要操作,暂时不用)