from pydantic import BaseModel,Field
from typing import Optional
from pydantic import ConfigDict

class UserRequest(BaseModel):
    username:str
    password:str


class UserInfoBase(BaseModel):
    "用户信息基础数据模型"
    nickname:Optional[str]=Field(None,max_length=255,description="用户昵称")
    avatar:Optional[str]=Field(None,max_length=255,description="用户头像URL")
    gender:Optional[str]=Field(None,max_length=10,description="用户性别")
    bio:Optional[str]=Field(None,max_length=255,description="个人简介")
#user_info对应的类:基础类（可选的）+Info类（id，用户名）
class UserInfoResponse(UserInfoBase):
    id:int
    username:str
    model_config=ConfigDict(
        from_attributes=True #允许从ORM模型类中直接赋值
    )
    
#data要有自己的数据类型
class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse = Field(...,alias='userInfo')

    #模型类配置
    model_config=ConfigDict(
        populate_by_name=True,#alias/字段名兼容
        from_attributes=True #允许从ORM模型类中直接赋值
    )

class UserUpdateRequest(BaseModel):
    "用户更新请求模型"
    nickname:str=None
    avatar:str=None
    gender:str=None
    bio:str=None
    phone:str=None

#前端传回的是newPassword，这里必须和前端传回来的参数名、数量均一致。
class UserChangePasswordRequest(BaseModel):
    #这里的alias是为了与前端的请求参数保持一致，oldPassword/newPassword/confirmPassword是前端的参数名
    old_password:str=Field(...,alias='oldPassword',description="旧密码")
    new_password:str=Field(...,min_length=6,alias='newPassword',description="新密码")