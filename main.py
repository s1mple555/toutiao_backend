from fastapi import FastAPI
import uvicorn
from routers import news
app=FastAPI()

@app.get("/")
def root():
    return {"message":"hello"}

@app.get("/hello/{name}")
def hello(name:str)->dict:
    return {"message":f"hello{name}"}
#挂载/注册路由，注意import导入news模块
app.include_router(news.router)

if __name__=='__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)