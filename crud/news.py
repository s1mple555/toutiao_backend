from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from models.news import Category,News
from sqlalchemy import func



async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
#result是一个列表，每个元素是一个元组，需要转换为category列表
# 输出：
# [(Category(id=1, name='科技', sort_order=1),), 
#  (Category(id=2, name='国际', sort_order=2),), 
#  (Category(id=3, name='体育', sort_order=3),)]
#通过scalars将结果转换为：
# [Category(id=1, name='科技', sort_order=1), 
#  Category(id=2, name='国际', sort_order=2), 
#  Category(id=3, name='体育', sort_order=3)]
    return result.scalars().all()

async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()

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
    

    
