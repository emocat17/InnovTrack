from fastapi import APIRouter

from app.core.dependency import DependPermisson

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .depts import depts_router
from .menus import menus_router
from .roles import roles_router
from .users import users_router
#这边开始是新加的
from .document import document_router #demo
from .arxiv_spider import arxiv_router #arxiv爬虫路由配置导入
from .arxiv_database import arxiv_database_router #arxiv论文本地数据导入
from .WIPO_spider import WIPO_spider_router #WIPO爬虫路由配置导入

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(users_router, prefix="/user", dependencies=[DependPermisson])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DependPermisson])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermisson])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DependPermisson])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermisson])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermisson])

#这边开始是新加的
v1_router.include_router(document_router, prefix="/document", dependencies=[DependPermisson]) #demo

v1_router.include_router(arxiv_router, prefix="/arxiv_spider", dependencies=[DependPermisson]) #arxiv论文爬虫

v1_router.include_router(arxiv_database_router, prefix="/arxiv_database",dependencies=[DependPermisson])

v1_router.include_router(WIPO_spider_router, prefix="/WIPO_spider", dependencies=[DependPermisson]) #WIPO专利爬虫
