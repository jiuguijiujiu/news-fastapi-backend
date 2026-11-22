# 导包
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1. 创建 数据库URL
# charset：字符编码
# utf8：一个字符最多存储3字节
# utf8mb4：一个字符最多存储4字节，真正且完整的utf-8
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"


# 2. 创建 异步引擎
async_engine = create_async_engine(
    url = ASYNC_DATABASE_URL,           # 数据库URL
    pool_size = 10,                     # 设置连接池中 保持的持久连接数
    max_overflow = 20,                  # 设置连接池中 允许创建的额外连接数
    echo = True                         # 可选：是否输出SQL日志
)


# 3. 创建 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind = async_engine,                    # 绑定异步引擎
    class_ = AsyncSession,                  # 指定会话类型：选择异步会话
    expire_on_commit = False                # 提交SQL指令后，ORM对象属性不会过期：不会重新查询数据库
)


# 4. 创建依赖项，用于获取数据库会话
async def get_db():
    """
    创建 数据库会话依赖项
    作用：为每个 HTTP 请求提供一个独立的异步数据库会话，并负责会话的提交、回滚与连接释放。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session                           # 返回/连接 会话
            await session.commit()                  # 统一将本次会话中所有的SQL指令 提交到数据库
        except Exception:
            await session.rollback()                # 出现异常，进行回滚，撤销本次会话中所有的SQL指令
            raise
        finally:
            await session.close()                   # 关闭/释放会话