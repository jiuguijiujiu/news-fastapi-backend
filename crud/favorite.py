from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import News


# 检查收藏状态: 当前用户 是否 收藏了这一条新闻
async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    # 是否有收藏记录
    return result.scalar_one_or_none() is not None


async def add_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 获取收藏列表: 获取的是某个用户的收藏列表 + 分页功能
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 总量
    count_stmt = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # 收藏的新闻列表：联表查询-join() + 按收藏时间排序-order_by() + 分页-offset().limit()
    # select(查询主体模型类, 字段别名).join(联合查询的模型类, 联合查询的条件).where().order_by().offset().limit()
    # 取别名: Favorite.created_at.label("favorite_time")
    skip = (page - 1) * page_size
    # 得到结果：
    # [
    #   (新闻对象, 收藏时间, 收藏id)
    # ]
    stmt = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
            .join(Favorite, Favorite.news_id == News.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip).limit(page_size)
            )
    result =  await db.execute(stmt)
    # 为什么不用scalars()：
    # scalars() 的强制特性：当 select 里面查了多个字段或对象时，scalars() 会只提取第一列（也就是你的 News 对象），把后面的 收藏时间 和 收藏id 全部丢弃！
    return result.all(), total


# 清空收藏列表: 当前用户的收藏列表
async def remove_all_favorites(db: AsyncSession, user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    # 返回删除的数量
    return result.rowcount or 0