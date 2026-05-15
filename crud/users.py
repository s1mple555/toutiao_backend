from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from models.users import User
from utils import security
from schemas.users import UserRequest,UserUpdateRequest,UserChangePasswordRequest
from models.users import UserToken
import uuid
from datetime import datetime, timedelta


async def get_user_by_username(db: AsyncSession, username: str) :
    query=select(User).where(User.username == username)
    result=await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserRequest) :
    # 先密码加密处理，之后再新增。
    hashed_password=security.get_hash_password(user_data.password)
    user=User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)#刷新，获取最新的user表数据
    return user

async def create_token(db: AsyncSession, user_id:int):
    #生成token，设置过期时间7天，查询数据库当前用户是否有token。有->更新，没有->添加。
    token=str(uuid.uuid4())
    expires_at=datetime.now()+timedelta(days=7,hours=0)#timedelta返回一个时间间隔
    query=select(UserToken).where(UserToken.user_id == user_id)#前面的代表UserToken表的user_id字段
    result=await db.execute(query)
    user_token=result.scalar_one_or_none()
    if user_token:#有则更新
        user_token.token=token
        user_token.expires_at=expires_at
    else:
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
    await db.commit()
    return token

async def authenticate_user(db:AsyncSession, username:str,password:str) :
    user=await get_user_by_username(db,username)
    if not user:
        return None
    if not security.verify_password(password,user.password):#后者是哈希过的密码
        return None
    return user#查出来了数据库中的user

async def get_user_by_token(db:AsyncSession, token:str) :
    query=select(UserToken).where(UserToken.token == token)#查询token表中是否有对应的token。
    result=await db.execute(query)
    db_token=result.scalar_one_or_none()
    #验证token是否存在，是否过期
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query=select(User).where(User.id == db_token.user_id)
    result=await db.execute(query)
    return result.scalar_one_or_none()#有令牌没过期，返回用户信息

async def update_user(db:AsyncSession,username:str,user_data:UserUpdateRequest):
    #为啥用username呢，是因为有get_user_by_username函数，能够根据用户名查询用户信息
    #user_data是前端传回来的user_data提交的表单信息。（类似于）
    #values中应该为字段=值，字段=值。
    #可以把user_data从pydantic类型转换为字典类型，用**就可以解包出来
    query=update(User).where(User.username==username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    #然而用户提交的内容可能有None，如果用户前端中为None的不进行更新
    result=await db.execute(query)
    await db.commit()

    #检查更新
    if result.rowcount==0:
        raise HTTPException(status_code=404,detail="用户不存在")
    #获取一下更新后的用户
    updated_user=await get_user_by_username(db,username)
    return updated_user

async def change_password(db:AsyncSession,user:User,old_password:str,new_password:str):#user是从浏览器前端拿到的token查到的
    if not security.verify_password(old_password,user.password):
        return False#旧密码错误
    hashed_new_pwd=security.get_hash_password(new_password)
    user.password=hashed_new_pwd
    db.add(user)#不是真的去创建一个用户，确保能够提交到数据库。防止session过期导致更新失败。
    #由SQLAlchemy接管这个user对象，确保在commit提交时能够更新数据库。
    await db.commit()#会话如果过期了这句就会失效
    await db.refresh(user)
    return True