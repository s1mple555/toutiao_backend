import asyncio
from typing import Dict,Any
from config.cache_conf import set_cache,get_json_cache
from typing import Optional

#新闻分类的读取和写入
CATEGORIES_KEY="news:categories"
NEWS_LIST_PREFIX="news_list"



# 获取新闻分类缓存，需要处理列表、字典等格式类型
async def get_cached_categories():
    categories=await get_json_cache(CATEGORIES_KEY)
    return categories
# data = [
#     {
#         "id": 1,                    # str -> int
#         "name": "科技",             # str -> str
#         "sort_order": 1,            # str -> int
#         "created_at": "2024-01-01"  # str -> str
#     }
# ]
# 写入新闻分类缓存，传入是ORM对象处理后的字典列表
async def set_cache_categories(data:list[Dict[str,Any]],expire:int=7200):
    result=await set_cache(CATEGORIES_KEY,data,expire)
    return result


# 写入新闻列表缓存，key名是"news_list:分类ID:页码:每页数量"
async def set_cache_news_list(category_id:Optional[int],page:int,size:int,news_list:list[Dict[str,Any]],expire:int=1800):
    #调用封装的函数，存入缓存
    category_part=category_id if category_id!=None else "all"
    key=f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}"
    return await set_cache(key,news_list,expire)

async def get_cache_news_list(category_id:Optional[int],page:int,size:int):
    category_part=category_id if category_id!=None else "all"
    key=f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}"
    return await get_json_cache(key)

