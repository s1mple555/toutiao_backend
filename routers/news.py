#放新闻模块所有路由
from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news
from config.db_config import get_db
#路由前缀，tags标签，用于在docs#交互式文档中分类显示
router=APIRouter(prefix="/api/news",tags=['news'])

@router.get("/categories")
async def get_categories(skip:int=0,limit:int=100,db:AsyncSession=Depends(get_db)):
    categories=await news.get_categories(db,skip,limit)
    # 要先获取数据库里里面新闻分类->定义模型类->封装查询数据的方法
    return {
        "code":200,
        "message":"获取新闻分类成功",
        "data":categories
    }
