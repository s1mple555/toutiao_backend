"""
数据库配置模块 - 异步数据库连接管理

整个数据库操作流程分为三个阶段：
1. 初始化阶段（应用启动时）：创建引擎和会话工厂
2. 请求处理阶段（每个 API 请求）：通过 get_db() 获取数据库会话
3. 清理阶段（请求结束时）：自动提交/回滚并关闭连接
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# ==================== 阶段 1: 初始化阶段 ====================
# 数据库连接 URL（应用启动时读取配置）
# 格式：mysql+aiomysql://用户名：密码@主机：端口/数据库名？charset=字符集
ASYNC_DATABASE_URL = "mysql+aiomysql://root:2919219501fh@localhost:3306/news_app?charset=utf8mb4"

# 创建异步数据库引擎（应用启动时只创建一次）
# 引擎是数据库连接的底层池，管理所有物理连接
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,      # 输出 SQL 语句到控制台（调试用，生产环境可关闭）
    pool_size=10,   # 连接池大小：保持 10 个长连接，避免频繁创建销毁
    max_overflow=20 # 最大溢出连接数：池满后最多额外创建 20 个临时连接
)

# 创建异步会话工厂（应用启动时只创建一次）
# AsyncSessionLocal 是一个"制造会话的机器"，每次调用它都会创建一个新的数据库会话
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,        # 绑定到上面创建的引擎
    class_=AsyncSession,      # 指定生成的会话类型为异步会话
    expire_on_commit=False    # commit 后不清空对象
)


# ==================== 阶段 2 & 3: 请求处理与清理阶段 ====================
# get_db 是一个异步生成器函数，用于 FastAPI 的依赖注入
# 每个 API 请求都会调用一次这个函数来获取数据库会话
async def get_db():
    """
    数据库会话依赖注入函数
    
    完整生命周期：
    1. 创建会话（进入 async with）
    2. 暂停并将会话交给 API 使用（yield）
    3. API 执行完毕后回来继续（yield 之后）
    4. 提交事务或回滚（根据是否异常）
    5. 关闭会话（finally）
    """
    
    # async with：异步上下文管理器
    # 进入时：自动创建数据库会话
    # 退出时：自动关闭会话（即使发生异常也会执行）
    async with AsyncSessionLocal() as session:
        try:
            # yield：暂停函数执行，把 session 对象返回给 API
            # 此时 API 函数开始执行，使用这个 session 进行数据库操作
            # 例如：result = await db.execute(select(User))
            yield session
            
            # 如果 API 执行成功（没有异常），提交所有数据库更改
            # 对于查询操作，commit 不是必须的，但统一处理无副作用
            await session.commit()
            
        except Exception as e:
            # 如果 API 执行过程中发生异常（如数据库错误、业务逻辑错误）
            # 回滚所有未提交的更改，保证数据一致性
            await session.rollback()
            
            # raise：重新抛出当前异常，让 FastAPI 知道出错了
            # 如果不写这行，异常会被"吞掉"，API 会返回 200 成功（实际失败了）
            raise
            
        finally:
            # finally：无论是否异常，这里一定会执行
            # 关闭会话，将数据库连接归还给连接池（不是真正关闭物理连接）
            # 这样连接可以被其他请求复用
            await session.close()