from pydantic import BaseModel,Field,ConfigDict
from models.favorite import Favorite
from schemas.base import NewsItemBase
from datetime import datetime

class FavoriteCheckResponse(BaseModel):
    if_favorite:bool =Field(...,alias='isFavorite')

class FavoriteAddRequest(BaseModel):#前端发来的请求参数是newsId
    news_id:int =Field(...,alias='newsId',description="新闻ID")

class FavoriteItemResponse(NewsItemBase):
    favorite_time: datetime = Field(..., alias="favoriteTime", description="收藏时间")
    favorite_id: int = Field(..., alias="favoriteId", description="收藏ID")

class FavoriteListResponse(BaseModel):
    rows:list[FavoriteItemResponse]=Field(...,alias='list',description="收藏列表")
    total:int=Field(...,alias='total',description="收藏总数")
    has_more:bool=Field(...,alias='hasMore',description="是否有更多数据")#前端约定的是has_More

    model_config=ConfigDict(populate_by_name=True,from_attributes=True)
