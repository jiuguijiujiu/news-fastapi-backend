from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class UserRequest(BaseModel):
    username: str = Field(default=..., description="用户名")
    password: str = Field(default=..., description="用户密码")


# user_info对应的类：基础类（UserInfoBase：存放可选的属性） + Info类（UserInfoResponse：继承基础类 + id、用户名）
class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    # 模型类配置
    model_config = ConfigDict(
        from_attributes = True          # 允许从 ORM对象属性中 取值
    )


# data数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(default=..., alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name = True,        # 别名与字段名兼容
        from_attributes = True          # 允许从 ORM对象属性中 取值
    )


# 更新用户信息模型类
class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None


class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(default=..., alias="oldPassword", description="旧密码")
    new_password: str = Field(default=..., min_length=6, alias="newPassword", description="新密码")