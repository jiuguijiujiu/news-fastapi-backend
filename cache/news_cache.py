# 新闻相关的缓存方法：新闻分类的读取和写入
from typing import Any, List, Dict, Optional
from config.cache_config import get_json_cache, set_cache


# key - value
NEWS_CATEGORIES_KEY = "news_categories"
NEWS_LIST_PREFIX = "news_list"


# 获取新闻分类缓存
async def get_cache_news_categories():
    return await get_json_cache(NEWS_CATEGORIES_KEY)


# 写入新闻分类缓存:缓存数据、过期时间
# 分类、配置 7200； 详情：1800； 列表：600； 验证码：120 -- 数据越稳定，缓存越持久
# 避免所有key同时过期 引起缓存雪崩
async def set_cache_news_categories(data: List[Dict[str, Any]], expire: int=7200):
    return await set_cache(NEWS_CATEGORIES_KEY, data, expire)


# 写入缓存-新闻列表 key = news_list:分类id:页码:每页数量 + 缓存数据 + 过期时间
async def set_cache_news_list(category_id: Optional[int], page: int, page_size: int, data: List[Dict[str, Any]], expire: int=1800):
    # 调用 封装的 Redis 的设置方法，存新闻列表到缓存
    category_part = category_id if category_id is not None else "all"       # 有的新闻没有分类id，设置为all
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{page_size}"
    return await set_cache(key, data, expire)


# 读取缓存-新闻列表
async def get_cache_news_list(category_id: Optional[int], page: int, page_size: int):
    category_part = category_id if category_id is not None else "all"       # 有的新闻没有分类id，设置为all
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{page_size}"
    return await get_json_cache(key)