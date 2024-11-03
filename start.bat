@echo off
echo Starting backend...
start cmd /k "python run.py"

rem 等待后端启动（可根据需要调整时间）
ping 127.0.0.1 -n 3 > nul  # 等待2秒

echo Starting frontend...
cd web
start cmd /k "pnpm dev"
