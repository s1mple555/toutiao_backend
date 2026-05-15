from fastapi import FastAPI
import uvicorn
from routers import news,users
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handles import register_exception_handlers
app=FastAPI()
#注册异常处理函数
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#允许所有来源，例如允许5173端口上的前端访问8000端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message":"hello"}


@app.get("/hello/{name}")
def hello(name:str)->dict:
    return {"message":f"hello{name}"}
#挂载/注册路由，注意import导入news模块
app.include_router(news.router)
app.include_router(users.router)
if __name__=='__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)