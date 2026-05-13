#放新闻模块所有路由
from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news
from fastapi import HTTPException
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
#Query参数，用于接收前端传递的查询参数
@router.get("/list")
async def get_news_list(
    category_id:int=Query(...,alias="categoryId"),#前端向list接口发请求，传来的参数为categoryId
    page:int=1,#返回第几页
    page_size:int=Query(10,le=100,alias="pageSize"),#每页数量
    db:AsyncSession=Depends(get_db)
):
    offset=(page-1)*page_size
    news_list=await news.get_news_list(db,category_id,offset,page_size)
    total=await news.get_news_count(db,category_id)
    hasMore=(offset+len(news_list))<total
    return{
        "code":200,
        "message":"获取新闻列表成功",
        "data":{
            "list":news_list,
            "total":total,
            "hasMore":hasMore
        }
    }


@router.get('/detail')#使用news模型类
async def read_news_detail(news_id:int=Query(...,alias="id"),db:AsyncSession=Depends(get_db)):
    news_detail=await news.get_news_detail(db,news_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")

    await news.increase_news_views(db,news_id)
    # await news.increase_news_views(db,news_detail.id)也可以
    related_news=await news.get_related_news(db,news_id,news_detail.category_id)
    return {#返回给前端，符合前端的驼峰命名规范。
        "code":200,
        "message":"获取新闻详情成功",
        "data":{
            "id":news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publishTime":news_detail.publish_time,
            "categoryId":news_detail.category_id,
            "views":news_detail.views,
            "relatedNews":related_news
        }
    }
