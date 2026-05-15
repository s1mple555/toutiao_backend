from sqlalchemy.ext.asyncio import AsyncSession
from models.history import History
from datetime import datetime
from sqlalchemy import select,func,delete
from models.news import News



async def add_history_crud(db:AsyncSession,user_id:int,news_id:int):
    #先查询user_id,news_id是否存在浏览记录
    history=await db.execute(select(History).where(History.user_id==user_id,History.news_id==news_id))
    existing_history=history.scalar_one_or_none()
    if existing_history:
        existing_history.view_time=datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=user_id, news_id=news_id)#数据库表添加事件默认是当前时间。
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

async def get_history_list_crud(db:AsyncSession,user_id:int,page:int,page_size:int):
    #查询user_id对应的浏览记录
    #查询总量
    total_count=await db.execute(select(func.count()).where(History.user_id==user_id))
    total_count=total_count.scalar_one_or_none()

    #联表查询User和history表，查询user_id对应的浏览记录
    #重命令的这些也是要查询的内容。并不仅仅只是重名了个名。
    query=(select(News,History.view_time.label("view_time"),History.id.label("history_id"))
                .join(History,History.news_id==News.id)
                .where(History.user_id==user_id)
                .order_by(History.view_time.desc())
                .offset((page-1)*page_size)
                .limit(page_size)
        )
    result=await db.execute(query)
    rows=result.all()
    return rows,total_count

async def delete_history_crud(db:AsyncSession,user_id:int,news_id:int):
    #查询user_id对应的浏览记录
    history=await db.execute(delete(History).where(History.user_id==user_id,History.news_id==news_id))
    await db.commit()
    return history.rowcount>0

async def clear_history_crud(db:AsyncSession,user_id:int):
    #查询user_id对应的浏览记录
    history=await db.execute(delete(History).where(History.user_id==user_id))
    await db.commit()
    return history.rowcount>0
