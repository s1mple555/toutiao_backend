from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from models.news import Category,News
from sqlalchemy import func
from cache.news_cache import get_cached_categories,set_cache_categories,get_cache_news_list,set_cache_news_list
from fastapi.encoders import jsonable_encoder
from schemas.base import NewsItemBase



async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    #先尝试从缓存中获取数据，没有再查库
    categories=await get_cached_categories()
    if categories:
        return categories#是否为 None，是否需要反序列化，在底层代码中已经处理了
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
#result 是一个列表，每个元素是一个元组，需要转换为 category 列表
# 输出：
# [(Category(id=1, name='科技', sort_order=1),), 
#  (Category(id=2, name='国际', sort_order=2),), 
#  (Category(id=3, name='体育', sort_order=3),)]
#通过 scalars 将结果转换为：
# [Category(id=1, name='科技', sort_order=1), 
#  Category(id=2, name='国际', sort_order=2), 
#  Category(id=3, name='体育', sort_order=3)]
    #写入缓存
    categories=result.scalars().all()
    #这里应该检查的是数据库查询执行结果result，而非缓存执行结果。
    if categories:
        categories=jsonable_encoder(categories)#ORM对象转换为字典列表
        await set_cache_categories(categories)
    return categories

async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    #页码=skip//limit+1
    page=skip//limit+1
    cached_list=await get_cache_news_list(category_id,page,limit)
    if cached_list:
        #要的是ORM格式，而不是保存的字典格式
        cached_list=[News(**item) for item in cached_list]
        return cached_list
    #没有缓存，再查库
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result=await db.execute(stmt)
    result=result.scalars().all()
    #写入缓存，先把ORM格式转换为字典格式
    if result:
        #不用别名，后端，redis不需要用驼峰规范
        #NewsItemBase先转为pydantic类型，model_validate从ORM对象item中提取属性值(至此转为pydantic类型)，model_dump转为字典类型，且不使用别名
        news_list=[NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in result]#转成python pydantic模型
    await set_cache_news_list(category_id,page,limit,news_list)
    return result

async def get_news_count(db:AsyncSession,category_id:int):#查询指定id新闻的数量
    stmt=select(func.count(News.id)).where(News.category_id==category_id)
    result=await db.execute(stmt)
    return result.scalar_one()#表示只能有1个结果，否则报错。

async def get_news_detail(db:AsyncSession,news_id:int):
    stmt=select(News).where(News.id==news_id)
    result=await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(db:AsyncSession,news_id:int):
    stmt=update(News).where(News.id==news_id).values(views=News.views+1)
    result=await db.execute(stmt)
    await db.commit()#一旦更新立即提交。数据库依赖注入那里是等待所有操作都完成后提交，不放心。
    #数据库更新操作之后，需要检查数据库真的命中了数据->命中了返回True，没命中返回False。
    return result.rowcount>0#rowcount可以获取到更新的行数

async def get_related_news(db:AsyncSession,news_id:int,category_id:int,limit:int=5):
    stmt=select(News).where(
        News.category_id==category_id, 
        News.id!=news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result=await db.execute(stmt)
    related_news=result.scalars().all()
    result=[{
        "id":news.id,
        "title":news.title,
        "content":news.content,
        "image":news.image,
        "author":news.author,
        "publishTime":news.publish_time,
        "categoryId":news.category_id,
        "views":news.views,
    } for news in related_news]
    return result
    

    
