import redis.asyncio as redis
import json

#定义变量获得服务器地址
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0

#创建redis的连接对象
redis_client=redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,#数据库编号
    decode_responses=True
)

#封装两种读取方法：1、字符串。2、列表/字典
#1、字符串
async def get_str_cache(key:str):
    try:
        value=await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None
    return value#返回字符串
#2、列表/字典，Redis中原本存储的所有内容都是字符串，要进行反序列化。
async def get_json_cache(key:str):
    try:
        value=await redis_client.get(key)
        if value:
            return json.loads(value)#把带引号的字典/列表转换为python中的列表/字典
        return None
    except Exception as e:#try语句中出现执行错误。
        print(f"获取Json格式缓存失败：{e}")
        return None

#设置缓存
async def set_cache(key:str,value:str,expire:int=3600):
    try:
        if isinstance(value,(dict,list)):
            value=json.dumps(value,ensure_ascii=False)#转成字符串之后再存。保留中文不转义，中文正常保存。
        else:
            value=str(value)
        await redis_client.setex(key, expire, value)
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return None
    return True
