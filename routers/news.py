#放新闻模块所有路由
from fastapi import APIRouter
#路由前缀，tags标签，用于在docs#交互式文档中分类显示
router=APIRouter(prefix="/api/news",tags=['news'])

@router.get("/categories")
def get_categories():
    return {"msg":"获取分类成功"}
