from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post(path="/add", description="添加历史记录")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    history_record = await history.add_news_history(db, user.id , data.news_id)
    return success_response(message="添加历史记录成功", data=history_record)


@router.get(path="/list", description="获取浏览历史列表")
async def get_history_list(
        page: int = Query(default=1, ge=1, description="页码"),
        page_size: int = Query(default=10, ge=1, le=100, alias="pageSize", description="每页条数"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [{
            **news.__dict__,
            "view_time": view_time,
        } for news, view_time in rows]
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取浏览历史列表成功", data=data)


@router.delete(path="/delete/{history_id}", description="删除单条浏览记录")
async def delete_history(
        history_id: int = Path(default=...),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.delete_news_history(db, user.id, history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除单条浏览记录成功")


@router.delete(path="/clear", description="清空浏览历史列表")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await history.delete_all_history(db, user.id)
    return success_response(f"删除{count}条历史记录")