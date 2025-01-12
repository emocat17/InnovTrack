<h1 align="center">InnovTrace</h1>

## 目前进度: 
 ### 论文采集(√)
 ### 论文数据库(√)
##### 访问

http://localhost:9999
username：admin
password：123456

### 本地启动
#### 后端
启动项目需要以下环境：
- Python 3.11

#### Pip 安装依赖
##### 本地环境
  1. 创建虚拟环境 /Conda
  ```sh
  python -m venv venv
  ```
  2. 激活虚拟环境
  ```sh
  source venv/bin/activate
  ```
##### conda环境
  1. 使用Anaconda Navigator直接Creat一个环境(记得选python 3.11+)
  2. 可以直接在安装界面搜索nodejs,安装 18.80+版本(我直接装的20.17)
  3. Pycharm右下角选择解释器/Vscode界面`Ctrl + Shift + P`之后搜索`python:选择解释器` 中点击刚配好的Conda环境
3. 安装依赖
```sh
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
我是用的requirements3.txt，让系统自行选择；
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
npm i -g pnpm # 已安装可忽略 ；如果安装不了请查找：npm换源
pnpm i # 或者 npm i    如果报错：”pnpm无法加载文件 。。。。系统禁止运行脚本“  错误，那么可以在windows电脑上打开PowerShell（管理员），输入“set-ExecutionPolicy RemoteSigned”后回车，再输入“Y”即可；
```


3. 启动
```sh
pnpm dev
```
# vue-fastapi-admin 模板使用

## 添加页面操作
- **后端**
  1. 在`app/models/admin.py`下新增数据库类(`tortoise`)
  2. 在`app/schemas/`下新增对应的数据（结构模型）验证文件，感觉适合与数据库联合起来做内容校验,不用的话这块不用写;这里使用了`Pydantic`进行定义数据模型，并使用这些模型对数据进行验证和转换。
  3. 在`app/controllers/`下增加操作文件，实现具体功能;供API中调用
  4. 注册路由:`app/api/v1/`下新增API文件夹及对应文件(新建`xxx`文件夹,内部含有`xxx.py`和`__init__.py`)，并相应修改`app/api/v1/__init__.py`; 主要使用了`fastapi`
  5. 在`app/core/init_app.py`中增加初始化操作;其实这块也不用改
  - 总的,来说,不需要其他操作的话,只要第`3`点和第`4`点就够了

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
    - 如果是`windows`的话,先注释掉`requirements.txt`中的`uvloop`  这个库在windows里没有;linux可以忽略此操作
    - `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
  - 启动服务：`python run.py`，服务现在应该正在运行，访问`http://localhost:9999/docs` 查看API文档

- **前端**
  - 进入前端目录 `cd web`
  - 安装依赖：`pnpm i` 或者 `npm i`
    - 如果网络不通可以先换源：
      ```
      pnpm config set registry https://registry.npmmirror.com
      ```
    - 还原源:
      ```
      pnpm config set registry https://registry.npmjs.org
      ```
    - 查看当前使用的源:
      ```
      pnpm get registry
      ```
  - 启动后访问 `http://localhost:3100/` 

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

---

## 实际开发教程参考文件中 `development.md`



# thanks
- `https://github.com/mizhexiaoxiao/vue-fastapi-admin` [原仓库](https://github.com/mizhexiaoxiao/vue-fastapi-admin)
- `jsly`
######################分割线######################################
# 本地文件转图数据库教程

- https://blog.csdn.net/wang_x_f911/article/details/139007588
- https://cloud.tencent.com/developer/article/2422349
# 下载测试文件(直接复制网址也行)
!wget "https://www.dropbox.com/scl/fi/g5ojyzk4m44hl7neut6vc/chinese_pdf.pdf?rlkey=45reu51kjvdvic6zucr8v9sh3&dl=1" -O chinese_pdf.pdf
# 获取LlamaCloud apikey
- https://cloud.llamaindex.ai/project/64141507-35b1-44f1-87f2-406252717444/api-key
# 获取OPenAI key 教程
- https://blog.csdn.net/qq_51447436/article/details/134624252


# Neo4j
neo4j console
- http://localhost:7474/
- neo4j://localhost:7687
- 账号密码:neo4j   /  12345678