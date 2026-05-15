from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any

def success_response(message:str='success',data:Any=None):
    #data传什么，就是什么。
    content={
        "code":200,
        "message":message,
        "data":data,
    }
    #data的类型不确定，例如：list,dict,set等。需要使用jsonable_encoder转换为jsonable的类型
    #这里没有使用fastapi隐式转换，因为fastapi会自动转换为jsonable的类型。
    return JSONResponse(content=jsonable_encoder(content))
