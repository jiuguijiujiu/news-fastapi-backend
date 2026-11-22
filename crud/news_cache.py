# 导包
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from cache.news_cache import get_cache_news_categories, set_cache_news_categories, set_cache_news_list, \
    get_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cache_news_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    # 执行
    result = await db.execute(stmt)
    categories = result.scalars().all()                 # ORM

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)       # ORM -> JSON
        await set_cache_news_categories(categories)

    # 返回数据
    return categories


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # 先尝试从缓存中获取新闻列表
    # 跳过的方法skip = (page - 1) * per_page // 每页数量 // 跳过的数量 // 每页数量 + 1
    # await get_cache_news_list(page, 页码, 每页数量)
    page = skip // limit + 1
    cache_list = await get_cache_news_list(category_id, page, limit)        # 缓存数据JSON
    if cache_list:
        # return cached_list  # 要的是 ORM，直接返回JSON其实也可以
        return [News(**item) for item in cache_list]

    # 查询指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()                 # ORM

    # 写入缓存
    if news_list:
        # 先把 ORM数据 转换 字典 转换 JSON才能写入缓存
        # ORM 转成 Pydantic，再转为 字典 转换 JSON
        # by_alias=False 不适用别名，保存 Python 风格，因为 Redis 数据是给后端用的
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    # 返回数据
    return news_list


async def get_news_count(db: AsyncSession, category_id: int):
    # 查询指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()              # 只能有一个结果，否则报错


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_new_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新 -> 检查数据库是否真的命中了数据 -> 命中了返回True
    return result.rowcount > 0                          # “操作回执单”：上面写着“本次操作实际变动了 X 行/条 数据”

async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    # order_by 排序 -> 浏览量和发布时间
    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),                          # 默认升序（asc），降序（desc）
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    # 列表推导式 推导出新闻的核心数据，然后再 return
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news]