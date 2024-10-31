# import uvicorn

# if __name__ == "__main__":
#     uvicorn.run(
#         "app:app",
#         host="0.0.0.0",
#         port=9999,
#         reload=True,
#         log_config="uvicorn_loggin_config.json"
#     )

import asyncio
import uvicorn

# 为 Windows 设置事件循环策略
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=9999,
        reload=True,
        log_config="uvicorn_loggin_config.json",
        loop="asyncio"  # 设置为原生 asyncio 事件循环
    )
