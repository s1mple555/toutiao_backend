from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def root():
    return {"message":"hello"}

@app.get("/hello/{name}")
def hello(name:str)->dict:
    return {"message":f"hello{name}"}
