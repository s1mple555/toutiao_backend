from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from config.db_config import get_db
from sqlalchemy import func
from models.news import News


#检查当前用户是否收藏了这条新闻
async def is_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
)->bool:
    query=select(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    result=await db.execute(query)
    #is not None 是为了返回一个布尔值
    return result.scalar_one_or_none() is not None

async def add_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
)->Favorite:
    favorite= Favorite(user_id=user_id,news_id=news_id)#构造出一个ORM对象，之后add。
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
)->Favorite:
#在Favorite表中查和删除
    query=delete(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    result=await db.execute(query)
    await db.commit()
    return result.rowcount>0#大于0说明删除成功，否则抛异常

async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    page: int=1,
    page_size: int=10,
):#要查到总量，收藏新闻的列表，（hasMore拿到路由里面做判断）
    count_query=select(func.count()).where(Favorite.user_id==user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one_or_none()

    #获取收藏列表->联表查询->按收藏时间排序->分页查询
    #query=select(查询主体模型类).join(联合查询模型类，联合查询条件).where.order_by().limit()
    query=(select(News,Favorite.created_at.label('favorite_time'),Favorite.id.label('favorite_id'))
                .join(Favorite,Favorite.news_id==News.id)
                .where(Favorite.user_id==user_id)
                .order_by(Favorite.created_at.desc())
                .offset((page-1)*page_size).limit(page_size))
    #一次查询出page_size条数据,offset从第几条数据开始返回。
    #在查询主体模型类，可以为重名字段起别名。
    result=await db.execute(query)
# """
# [主题模型类查询结果+联合查询模型类结果
#     (新闻对象,收藏时间,收藏ID),
#     (新闻对象,收藏时间,收藏ID),
#     ...
# ]
# """
    rows=result.all()
    return rows,total

async def remove_all_favorite(
    db: AsyncSession,
    user_id: int,
)->bool:
    query=delete(Favorite).where(Favorite.user_id==user_id)
    result=await db.execute(query)
    await db.commit()
    return result.rowcount or 0
#大于0说明删除成功，否则抛异常