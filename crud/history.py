from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.history import History
from datetime import datetime
from models.news import News


async def add_news_history(db: AsyncSession, user_id: int, news_id: int):
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    history_record = result.scalar_one_or_none()

    if not history_record:
        history_record = History(user_id=user_id, news_id=news_id)
        db.add(history_record)
    else:
        history_record.view_time = datetime.now()

    # flush(): 执行 SQL 语句，但未提交事务（数据在内存中，可回滚）
    # commit(): 执行 SQL 语句，并提交事务，数据永久落盘（不可回滚）
    await db.flush()
    await db.refresh(history_record)
    return history_record


async def get_history_list(db: AsyncSession, user_id: int, page: int, page_size: int):
    count_stmt = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    skip = (page - 1) * page_size
    # 得到结果：
    # [
    #   (新闻对象, 浏览历史时间)
    # ]
    stmt = (select(News, History.view_time)
            .join(History, History.news_id == News.id)
            .where(History.user_id == user_id)
            .order_by(History.view_time.desc())
            .offset(skip).limit(page_size)
            )
    result = await db.execute(stmt)
    return result.all(), total


async def delete_news_history(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


async def delete_all_history(db: AsyncSession, user_id: int):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount or 0