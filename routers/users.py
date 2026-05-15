from fastapi import APIRouter,Depends,HTTPException,status
from config.db_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest
from crud import users
from utils.response import success_response
from schemas.users import UserAuthResponse,UserInfoResponse,UserChangePasswordRequest
from utils.auth import get_current_user
from models.users import User
from schemas.users import UserUpdateRequest



router=APIRouter(prefix="/api/user",tags=["user"])

@router.post('/register')#传入用户信息，数据库依赖项
async def register(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    #注册逻辑：验证用户是否存在，创建用户，生成token，响应结果
    existing_user=await users.get_user_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户名已存在")
    #如果得到的是None，那么可以注册用户
    user=await users.create_user(db,user_data)
    #user表,user_token表
    token=await users.create_token(db,user.id)
    #直接return，如果需要修改某个字段，全部项目都需要修改
    # return {
    #     "code":200,
    #     "message":"注册成功",
    #     "data":{
    #         "token":token,
    #         "userInfo":{
    #             "id":user.id,
    #             "username":user.username,
    #             "bio":user.bio,
    #             "avatar":user.avatar,
    #         }
    #     }
    # }
    response_data=UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user)#将ORM模型类转换为UserInfoResponse模型类
    )
    return success_response(message="注册成功",data=response_data)

@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    # 验证用户是否存在，验证密码是否正确，生成token，响应结果
    user=await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        #具体业务错误，需要具体来写。
        #全局异常处理器就是规定响应格式。
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名/密码错误")
    token = await users.create_token(db,user.id)
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data) 

@router.get("/info")
async def get_user_info(user:User=Depends(get_current_user)):#依赖注入，能够拿到注入函数的参数和返回值（只能拿到返回值，拿不到db）
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/update")
async def update_user_info(user_data:UserUpdateRequest,user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    #user的depends注入能够拿到当前的token和db
    user=await users.update_user(db,user.username,user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
    user_data:UserChangePasswordRequest,
    user:User=Depends(get_current_user),#获取浏览器传来的token，并从token获得当前user
    db:AsyncSession=Depends(get_db)
):
#验证token是否有效
    success=await users.change_password(db,user,old_password=user_data.old_password,new_password=user_data.new_password)
    if success:
        return success_response(message="修改密码成功")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败")
