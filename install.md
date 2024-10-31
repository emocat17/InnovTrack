# vue-fastapi-admin 模板使用

1. **后端目录解析**
   - `app/models`：主要是定义数据库模型
   - `app/schemas`：主要是定义数据库之外的一些模型，例如对应api请求数据时，用一个账号密码模型等
   - `app/controllers`：控制器，定义一些模型对应的操作，如用户的crud、api的刷新之类的
   - `app/core`：核心功能，全局的crud、后台任务、上下文、初始化等的管理，异步编程中的上下文管理使用了contextvars


2. **要添加模块**
   - **后端**
     1. 增加对应的数据库数据，`app/models/admin.py`下新增数据库类，这里使用了tortoise进行数据库操作
     2. 在`app/schemas/`下新增对应的数据（结构模型）验证文件，这里使用了Pydantic进行定义数据模型，并使用这些模型对数据进行验证和转换。
     3. 在`app/controllers/`下增加模块操作文件，主要是供api中调用
     4. 注册路由，`app/api/v1/`下新增api文件夹及对应文件，并相应修改`app/api/v1/__init__.py`，这里使用了fastapi
     5. 在`app/core/init_app.py`中增加初始化操作
   - **前端**
     1. 在`web/src/api/index.js`中增加api的接口定义
     2. 在`web/src/routes/index.js`中新增页面路由
     3. 在`web/src/views`中合适位置新增页面即可




3. **运行**
   - **后端**
     - 模板依赖python3.11
     - 安装虚拟环境（项目根目录执行）：`python -m venv venv`
     - 激活虚拟环境：`venv\scripts\activate`
     - 当然使用Conda也可以
     - 安装库：
       ```bash
       # 先注释掉requirements.txt中的uvloop
       pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
       # 启动服务：`python run.py`，服务现在应该正在运行，访问`http://localhost:9999/docs`查看API文档
       ```
   - **前端**
     - 模板依赖node v18.8.0+
     - 进入前端目录`cd web`
     - 安装依赖（建议使用pnpm）：https://pnpm.io/zh/installation/
       ```bash
       # 已安装可忽略
       npm i -g pnpm # 已安装可忽略
       pnpm i # 或者 npm i
       # 如果网络不通可以先换源：
       ```
     - 换淘宝源：
       ```bash
       pnpm config set registry https://registry.npmmirror.com
       # 还原:
       pnpm config set registry https://registry.npmjs.org
       # 查看当前使用的源:
       pnpm get registry
       ```
     - 启动（在web目录下）：`pnpm dev`，访问`http://localhost:3100/`即可查看网页


   - windows上，在`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`需要先注释掉requirements.txt中的uvloop，这个库不支持windows，主要用于优化协程的事件循环，不安装也不影响运行
   - 模板的创建api功能（指网页上的）是能创建api记录，但是因为没有路由和控制器，是没有用的。