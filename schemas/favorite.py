from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(default=..., alias="isFavorite")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(default=..., alias="newsId")


# 规划两个类： 一个是新闻模型类 + 收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name = True,            # 兼容别名
        from_attributes=True                # 允许从orm对象中提取属性值
    )


# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int = Field(default=0)
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name = True,            # 兼容别名
        from_attributes=True                # 允许从orm对象中提取属性值
    )