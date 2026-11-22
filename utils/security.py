# 导包
from passlib.context import CryptContext

# 创建加密上下文
pwd_context = CryptContext(
    schemes = ["bcrypt"],           # 加密算法
    deprecated = "auto"             # 新旧加密算法自适应
)


# 密码加密
def get_hash_password(password: str):
    return pwd_context.hash(password)


# 密码验证：返回值为bool类型
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)