# 导包
from fastapi import APIRouter, Depends, Query, HTTPException
from crud import news, news_cache
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# 1. 创建 APIRouter实例
# prefix：路由前缀
# tags：分组/标签
router = APIRouter(prefix="/api/news", tags=["news"])


# 接口实现流程
# 1. 模块化路由 -> 参考 API接口规范文档
# 2. 定义模型类 -> 参考 数据库表结构 (数据库设计文档)
# 3. 数据库CRUD -> 封装数据库CRUD方法
# 4. 路由调用逻辑 -> 路由处理函数 注入并调用 封装好的CRUD方法，然后响应结果


# 2. 创建 api接口
@router.get(path="/categories", description="获取新闻分类列表")
async def get_categories(skip: int=0, limit: int=100, db: AsyncSession = Depends(get_db)):
    # 先获取数据库里面 新闻分类数据 —> 先定义模型类 —> 封装查询数据的方法
    categories = await news_cache.get_categories(db=db, skip=skip, limit=limit)
    return {
        "code": 200,
        "message": "获取新闻分类列表成功",
        "data": categories
    }


@router.get(path="/list", description="获取新闻列表")
async def get_news_list(
        category_id:int = Query(default=..., alias="categoryId"),
        page: int = 1,
        page_size:int = Query(default=10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)
):
    # 思路：处理分页规则 ——> 查询新闻列表 ——> 计算新闻总量 ——> 判断是否还有更多新闻
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    # 判断是否还有更多新闻：(跳过的 + 当前列表里面的数量) < 总量
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }


@router.get(path="/detail", description="获取新闻详情")
async def get_news_detail(
        news_id: int = Query(default=..., alias="id"),
        db: AsyncSession = Depends(get_db)
):
    # 获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_res = await news.increase_new_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "获取新闻详情成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }