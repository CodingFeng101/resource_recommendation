# Resource Recommendation System

智能资源推荐系统后端API

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   └── recommendation/     # 推荐模块
│       ├── api/           # API路由
│       ├── crud/          # 数据访问层
│       ├── model/         # 数据模型
│       ├── schema/        # 数据验证模式
│       └── service/       # 业务逻辑层
├── common/                # 公共模块
│   ├── exception.py       # 异常定义
│   ├── exception_handlers.py # 异常处理器
│   ├── middleware.py      # 中间件
│   └── llm/              # LLM相关
├── core/                  # 核心配置
│   ├── config.py         # 应用配置
│   └── logging.py        # 日志配置
├── database/              # 数据库配置
│   └── db_mysql.py       # 数据库连接
└── migrations/            # 数据库迁移
```

## 快速开始

### 1. 环境配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入配置信息：
- 数据库连接信息
- OpenAI API密钥
- 其他服务配置

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
# 初始化迁移（仅首次运行）
alembic init migrations

# 创建迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
python main.py
```

或使用uvicorn：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能

- **Report管理**: 创建、查询、更新、删除报告数据
- **Embedding管理**: 向量数据的存储和检索
- **关联查询**: Report和Embedding的关联查询
- **统一异常处理**: 标准化的错误响应
- **请求日志**: 完整的请求追踪和日志记录

## 环境变量配置

### 必填配置
```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
```

### 可选配置
```env
# 调试模式
DEBUG=false

# 日志级别
LOG_LEVEL=INFO

# 服务器配置
HOST=0.0.0.0
PORT=8000
```
