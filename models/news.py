# 导包
# Mapped：设置/映射 属性类型， mapped_column：设置/映射 字段
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Index, Text, ForeignKey
from typing import Optional


# 定义模型基类
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,                                       # 设置字段类型，可以不写，因为有Mapped[datetime]：设置/映射 属性类型
        default=datetime.now,
        comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,                           # 插入时的默认值：是datetime.now 对象，而不是datetime.now() 执行结果
        onupdate=datetime.now,                          # 修改时的默认值：是datetime.now 对象，而不是datetime.now() 执行结果
        comment="更新时间"
    )


# 定义模型类
class Category(Base):
    # 设置表名
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")

    # __repr__ 魔法方法：用 print() 打印对象时，自动调用
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"


class News(Base):
    __tablename__ = "news"

    # 创建索引：提升查询/排序速度
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),   # 高频 按新闻分类查询 场景
        Index('idx_publish_time', 'publish_time')       # 高频 按发布时间排序 场景
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"