# 今日头条新闻后端（FastAPI）

基于 **FastAPI + SQLAlchemy 2.0（异步）+ MySQL + Redis** 实现的新闻资讯类应用后端服务，为移动端新闻前端提供完整的 RESTful API，涵盖用户认证、新闻浏览、收藏与浏览历史等核心业务。

---

## 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [使用说明](#使用说明)
- [项目结构](#项目结构)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目概述

### 整体定位

本项目是一个仿"今日头条"移动端资讯应用的**后端 API 服务**（学习实践项目），前端为已完成的 Vue 单页应用，本仓库仅实现 FastAPI 后端部分。

### 核心业务功能

| 模块 | 功能 |
| --- | --- |
| 用户（users） | 用户注册、登录、基于 Token 的身份认证、查询/修改用户信息、修改密码 |
| 新闻（news） | 新闻分类列表、分页新闻列表、新闻详情、浏览量自增、相关新闻推荐 |
| 收藏（favorite） | 检查收藏状态、添加/取消收藏、分页收藏列表、清空收藏 |
| 历史（history） | 记录浏览历史、分页历史列表、删除单条/清空历史 |

### 设计目标与架构特点

- **全异步架构**：基于 `asyncio`，数据库访问使用 SQLAlchemy 2.0 `AsyncSession` + `aiomysql`，缓存访问使用 `redis.asyncio`，充分利用 FastAPI 的异步并发能力。
- **经典分层架构**：`routers`（路由层）→ `crud`（数据访问层）→ `models`（ORM 模型层），`schemas`（Pydantic 校验层）与 `utils`（公共工具层）横向支撑，职责单一、依赖清晰。
- **缓存旁路（Cache-Aside）模式**：新闻分类与新闻列表优先读 Redis，未命中时回源 MySQL 并异步回填缓存，按数据稳定性设置差异化过期时间。
- **统一响应与异常处理**：所有接口遵循 `{code, message, data}` 统一响应结构；全局注册 `HTTPException`、`IntegrityError`、`SQLAlchemyError` 与兜底异常处理器，屏蔽底层错误细节。

---

## 技术栈

| 类别 | 技术 | 版本要求 | 说明 |
| --- | --- | --- | --- |
| 语言 | Python | ≥ 3.10（开发环境 3.13） | 需支持 `asyncio` 与新式类型注解 |
| Web 框架 | FastAPI | 0.141.x | RESTful API 框架，自带 OpenAPI/Swagger 文档 |
| ASGI 服务器 | Uvicorn | 0.52.x | 异步应用服务器 |
| ORM | SQLAlchemy | 2.0.x | 使用 `DeclarativeBase` / `Mapped` / `AsyncSession` |
| 数据库驱动 | aiomysql | 0.3.x | MySQL 异步驱动 |
| 数据库 | MySQL | 8.0+ | 字符集要求 `utf8mb4` |
| 缓存 | Redis（redis-py asyncio） | 服务端 6+ / 客户端 8.x | 新闻分类与列表缓存 |
| 数据校验 | Pydantic | 2.x（随 FastAPI 安装） | 请求/响应模型定义与校验 |
| 密码加密 | passlib + bcrypt | passlib 1.7.4 / bcrypt 4.0.1 | 密码哈希存储（注意：`passlib 1.7.4` 需搭配 `bcrypt==4.0.1`） |

---

## 快速开始

### 环境依赖

- Python 3.10 及以上
- MySQL 8.0 及以上
- Redis 6.0 及以上
- pip（随 Python 附带）

### 1. 获取代码

```bash
git clone <仓库地址>
cd toutiao_backend
```

### 2. 创建虚拟环境并安装依赖

```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install fastapi==0.141.1 uvicorn==0.52.4 sqlalchemy==2.0.43 aiomysql==0.3.2 redis==8.1.0 passlib==1.7.4 bcrypt==4.0.1
```

> 提示：`bcrypt` 必须锁定 `4.0.1` 版本，`passlib 1.7.4` 与 `bcrypt >= 4.1` 存在兼容性问题。

### 3. 初始化数据库

1. 启动 MySQL 服务，创建数据库（表结构与 `models/` 下的 ORM 模型一一对应）：

   ```sql
   CREATE DATABASE IF NOT EXISTS news_app DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```

2. 依次创建以下数据表：`user`、`user_token`、`news_category`、`news`、`favorite`、`history`，并导入新闻与分类测试数据。

### 4. 修改配置

项目配置以模块级常量方式集中管理：

- **MySQL 连接**：编辑 [db_conf.py](file:///d:/code/黑马FastAPI/toutiao_backend/config/db_conf.py) 中的 `ASYNC_DATABASE_URL`，格式为：

  ```
  mysql+aiomysql://<用户名>:<密码>@<主机>:<端口>/news_app?charset=utf8mb4
  ```

- **Redis 连接**：编辑 [cache_config.py](file:///d:/code/黑马FastAPI/toutiao_backend/config/cache_config.py) 中的 `REDIS_HOST`、`REDIS_PORT`、`REDIS_DB`。

### 5. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后：

- 服务地址：<http://127.0.0.1:8000>
- 交互式 API 文档（Swagger UI）：<http://127.0.0.1:8000/docs>
- ReDoc 文档：<http://127.0.0.1:8000/redoc>

---

## 使用说明

### 统一响应格式

所有接口均返回如下 JSON 结构：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 身份认证机制

1. 注册或登录成功后，服务端生成 UUID Token（有效期 7 天）并写入 `user_token` 表，随响应返回。
2. 访问需要登录的接口时，在请求头携带：

   ```
   Authorization: Bearer <token>
   ```

3. Token 缺失、无效或过期时返回 `401`。

### API 接口一览

| 方法 | 路径 | 说明 | 是否需要登录 |
| --- | --- | --- | --- |
| POST | `/api/user/register` | 用户注册 | 否 |
| POST | `/api/user/login` | 用户登录 | 否 |
| GET | `/api/user/info` | 获取当前用户信息 | 是 |
| PUT | `/api/user/update` | 修改用户信息（昵称/头像/性别/简介/手机号） | 是 |
| PUT | `/api/user/password` | 修改密码（新密码至少 6 位） | 是 |
| GET | `/api/news/categories` | 获取新闻分类列表 | 否 |
| GET | `/api/news/list` | 分页获取新闻列表（`categoryId`、`page`、`pageSize`） | 否 |
| GET | `/api/news/detail` | 获取新闻详情（浏览量 +1，含相关新闻） | 否 |
| GET | `/api/favorite/check` | 检查新闻收藏状态（`newsId`） | 是 |
| POST | `/api/favorite/add` | 添加收藏 | 是 |
| DELETE | `/api/favorite/remove` | 取消收藏（`newsId`） | 是 |
| GET | `/api/favorite/list` | 分页获取收藏列表 | 是 |
| DELETE | `/api/favorite/clear` | 清空收藏列表 | 是 |
| POST | `/api/history/add` | 添加浏览记录 | 是 |
| GET | `/api/history/list` | 分页获取浏览历史 | 是 |
| DELETE | `/api/history/delete/{history_id}` | 删除单条浏览记录 | 是 |
| DELETE | `/api/history/clear` | 清空浏览历史 | 是 |

### 常用操作示例

**1. 注册 / 登录**

```bash
curl -X POST http://127.0.0.1:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "***"}'
```

登录接口路径为 `/api/user/login`，请求体相同。响应 `data` 中包含 `token` 与 `userInfo`。

**2. 获取新闻分类与列表**

```bash
# 分类列表
curl http://127.0.0.1:8000/api/news/categories

# 某分类下第 1 页新闻（每页 10 条，pageSize 最大 100）
curl "http://127.0.0.1:8000/api/news/list?categoryId=1&page=1&pageSize=10"
```

**3. 携带 Token 操作收藏**

```bash
# 添加收藏
curl -X POST http://127.0.0.1:8000/api/favorite/add \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"newsId": 1}'

# 查询收藏列表
curl "http://127.0.0.1:8000/api/favorite/list?page=1&pageSize=10" \
  -H "Authorization: Bearer <token>"
```

> 注意：请求体与查询参数中的字段采用 **camelCase** 命名（如 `newsId`、`pageSize`、`categoryId`），由 Pydantic 别名映射至后端的 snake_case 字段。

### 与前端联调

项目已在 [main.py](file:///d:/code/黑马FastAPI/toutiao_backend/main.py) 中配置 `CORSMiddleware`（开发环境允许所有来源），前端应用直接请求 `http://127.0.0.1:8000` 即可联调。**正式上线前应将 `allow_origins` 收敛为具体域名。**

---

## 项目结构

```text
toutiao_backend/
├── main.py                      # 应用入口：创建 FastAPI 实例、注册路由/异常处理器/CORS 中间件
├── test_main.http               # HTTP 接口快速测试文件（IDE 可直接运行）
├── config/                      # 全局配置
│   ├── db_conf.py               # MySQL 异步引擎、会话工厂与 get_db 依赖项
│   └── cache_config.py          # Redis 异步客户端与通用缓存读写封装
├── models/                      # SQLAlchemy ORM 模型（表结构定义）
│   ├── users.py                 # user、user_token 表
│   ├── news.py                  # news_category、news 表
│   ├── favorite.py              # favorite 表
│   └── history.py               # history 表
├── schemas/                     # Pydantic 请求/响应模型
│   ├── base.py                  # 新闻条目公共基础模型 NewsItemBase
│   ├── users.py                 # 用户注册/登录/信息/改密模型
│   ├── favorite.py              # 收藏相关模型
│   └── history.py               # 浏览历史相关模型
├── crud/                        # 数据访问层：封装数据库 CRUD 操作
│   ├── users.py                 # 用户增查改、密码校验、Token 生成与验证
│   ├── news.py                  # 新闻分类/列表/详情/浏览量/相关新闻查询
│   ├── news_cache.py            # 新闻分类与列表的"缓存旁路"查询逻辑
│   ├── favorite.py              # 收藏增删查与分页
│   └── history.py               # 浏览历史增删查与分页
├── cache/                       # 缓存 Key 管理与读写方法
│   └── news_cache.py            # 新闻分类/列表缓存的 key 规则与过期策略
└── utils/                       # 公共工具
    ├── auth.py                  # get_current_user 依赖项：解析 Bearer Token 并注入当前用户
    ├── security.py              # bcrypt 密码加密与校验
    ├── response.py              # success_response 统一成功响应封装
    ├── exception.py             # 各类异常处理器实现
    └── exception_handlers.py    # 全局异常处理器注册
```

---

## 贡献指南

欢迎提交 Issue 和 Pull Request，请遵循以下流程与规范。

### 贡献流程

1. **Fork 本仓库**并克隆到本地。
2. **创建特性分支**：`git checkout -b feature/<简短描述>`。
3. **开发与自测**：使用 `uvicorn main:app --reload` 启动服务，通过 `/docs` 或 `test_main.http` 验证接口行为。
4. **提交变更**：`git commit -m "feat: 添加新闻收藏批量删除接口"`。
5. **推送并发起 Pull Request**，在描述中说明变更动机与影响范围，等待代码评审。

### 提交信息规范

采用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

| 前缀 | 用途 |
| --- | --- |
| `feat` | 新功能 |
| `fix` | 缺陷修复 |
| `refactor` | 重构（不改变外部行为） |
| `docs` | 文档变更 |
| `test` | 测试相关 |
| `chore` | 构建/依赖/杂项 |

### 编码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)，缩进 4 空格，标识符使用 `snake_case`，类名使用 `PascalCase`。
- **严格分层**：路由层（`routers`）只做参数接收与响应组装，数据库操作必须下沉到 `crud` 层，禁止在路由函数中直接编写 SQL/ORM 语句。
- **请求/响应模型**：入参与出参一律通过 `schemas` 中的 Pydantic 模型定义，对外字段使用 camelCase 别名，内部字段使用 snake_case。
- **统一响应**：成功响应使用 `utils.response.success_response`；业务错误抛出 `HTTPException`，由全局异常处理器统一转换。
- **异步优先**：涉及数据库、Redis、网络 I/O 的函数一律声明为 `async`，禁止在异步上下文中使用阻塞调用。
- 新增接口需同步在路由装饰器中填写 `description`，保证 OpenAPI 文档可读性。

---

## 许可证

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源，允许在保留版权声明的前提下自由使用、修改与分发。
