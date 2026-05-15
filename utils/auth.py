#根据token查询用户，最终返回用户信息。
from fastapi import Header,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crud import users
from models.users import User
from fastapi import HTTPException,status
from config.db_config import get_db


async def get_current_user(authorization:str=Header(...,alias="Authorization"),db:AsyncSession=Depends(get_db)) :
    #Bearer xxxx
    #token=authorization.split(" ")[1]#0是Bearer，1是token，莫名其妙报错。
    token=authorization.replace("Bearer ","")
    user=await users.get_user_by_token(db,token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效令牌或过期")
    return user
