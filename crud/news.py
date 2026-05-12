from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.news import Category

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