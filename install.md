
### 运行
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
    npm i -g pnpm # 已安装可忽略
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