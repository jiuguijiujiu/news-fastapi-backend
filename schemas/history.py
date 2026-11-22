from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id: int = Field(default=..., alias="newsId")


class HistoryNewsItemResponse(NewsItemBase):
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        populate_by_name = True,
        from_attributes = True
    )


class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int = Field(default=0)
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name = True,            # 兼容别名
        from_attributes=True                # 允许从orm对象中提取属性值
    )