from fastapi import APIRouter,Depends,status,HTTPException
from schemas.history import HistoryAddRequest
from crud import history
from utils.auth import get_current_user
from config.db_config import get_db
from schemas.history import HistoryNewsItemResponse,HistoryListResponse
from fastapi import Query,Request
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response import success_response
router=APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(
    data:HistoryAddRequest,
    user:User=Depends(get_current_user),
    db:AsyncSession=Depends(get_db),
):
    result=await history.add_history_crud(db,user.id,data.news_id)
    return success_response(message=f"添加了历史记录",data=result)

@router.get("/list")
async def get_history_list(
    page:int=Query(1,ge=1),
    page_size:int=Query(10,ge=1,le=100,alias="pageSize"),
    user:User=Depends(get_current_user),
    db:AsyncSession=Depends(get_db)
):
    rows,total_count=await history.get_history_list_crud(db,user.id,page,page_size)
    has_more=total_count>page*page_size
    history_list = [HistoryNewsItemResponse.model_validate({
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id
    }) for news, view_time, history_id in rows]
    result=HistoryListResponse(
        list=history_list,
        total=total_count,
        has_more=has_more
    )
    return success_response(message=f"success",data=result)

#delete方法用那种参数呢？请求体参数、路径参数、查询参数中的哪种？还是都可以？
@router.delete("/delete/{news_id}")
async def delete_history(
    news_id:int,
    user:User=Depends(get_current_user),
    db:AsyncSession=Depends(get_db)
):
    result=await history.delete_history_crud(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message=f"删除了历史记录")#这个接口返回时不需要data。文档规定。

@router.delete("/clear")
async def clear_history(
    user:User=Depends(get_current_user),
    db:AsyncSession=Depends(get_db)
):
    result=await history.clear_history_crud(db,user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message=f"清空了历史记录")