# 智能教育资源推荐系统

## 项目概述

这是一个基于RAG（Retrieval-Augmented Generation）技术的智能教育资源推荐系统，专为教育场景设计，能够智能分析教学视频内容，生成学习报告，并提供基于语义理解的资源推荐服务。

## 🌟 核心功能

### 1. 智能内容分析
- **视频摘要生成**: 自动分析教学视频，生成结构化的学习摘要
- **学习报告生成**: 基于对话内容生成详细的学习报告，包含知识点、时间段、关键要点等
- **标签生成**: 为学习内容自动生成相关标签，便于分类和检索

### 2. 语义搜索与推荐
- **课程语义搜索**: 基于用户查询的语义理解，推荐最相关的课程
- **报告语义搜索**: 在特定课程内搜索最相关的学习报告
- **向量相似度计算**: 使用先进的embedding技术实现高精度匹配

### 3. 数据管理
- **课程管理**: 支持多种教育资源的导入和管理
- **报告管理**: 学习报告的存储、检索和分析
- **标签管理**: 智能标签系统的维护和优化

## 🛠️ 技术架构

### 后端技术栈
- **框架**: FastAPI (异步高性能Web框架)
- **数据库**: MySQL + SQLAlchemy (ORM)
- **向量计算**: scikit-learn + NumPy
- **AI/ML**: 自定义LLM集成，支持多种embedding模型
- **异步处理**: asyncio + asyncpg

### 项目结构
```
backend/
├── app/
│   └── recommendation/
│       ├── api/              # API路由层
│       │   ├── router.py     # 主路由配置
│       │   └── v1/
│       │       └── recommendation/
│       │           └── rag_api.py  # RAG相关API端点
│       ├── crud/             # 数据访问层 (CRUD操作)
│       │   ├── course.py     # 课程数据操作
│       │   ├── report.py     # 报告数据操作
│       │   ├── video_summary.py  # 视频摘要数据操作
│       │   ├── report_embedding.py  # 报告向量数据操作
│       │   └── summary_embedding.py # 摘要向量数据操作
│       ├── model/            # SQLAlchemy数据库模型
│       │   ├── base.py       # 基础模型类
│       │   ├── course.py     # 课程模型
│       │   ├── report.py     # 报告模型
│       │   ├── video_summary.py    # 视频摘要模型
│       │   ├── report_embedding.py # 报告向量模型
│       │   └── summary_embedding.py # 摘要向量模型
│       ├── schema/           # Pydantic数据验证模型
│       │   ├── course.py     # 课程数据模型
│       │   ├── report.py     # 报告数据模型
│       │   ├── video_summary.py    # 视频摘要数据模型
│       │   ├── report_embedding.py # 报告向量数据模型
│       │   └── summary_embedding.py # 摘要向量数据模型
│       └── services/         # 业务逻辑层
│           ├── course_service.py    # 课程业务逻辑
│           ├── report_service.py    # 报告业务逻辑
│           ├── video_summary_service.py # 视频摘要业务逻辑
│           ├── report_embedding_service.py # 报告向量业务逻辑
│           ├── summary_embedding_service.py # 摘要向量业务逻辑
│           └── rag_service.py       # RAG核心服务
├── common/                   # 公共组件
│   └── core/
│       └── rag/              # RAG核心组件
│           └── retrieval/    # 检索相关组件
├── core/                     # 核心配置
├── database/                 # 数据库配置
│   └── db_mysql.py          # MySQL数据库连接配置
└── main.py                   # FastAPI应用入口
```

## 📋 数据模型

### 核心实体

#### Course (课程表)
- **uuid**: 课程唯一标识符 (主键)
- **course_id**: 课程ID (唯一索引)
- **resource_name**: 资源名称
- **file_name**: 文件名
- **grade**: 年级 (索引)
- **subject**: 学科 (索引)
- **video_link**: 视频链接 (可选)
- **learning_objectives**: 学习目标 (可选)
- **learning_style_preference**: 学习方式偏好 (可选)
- **knowledge_level_self_assessment**: 知识掌握程度自评 (可选)
- **dialogue**: 课程对话数据 (JSON格式)
- **created_at/updated_at**: 创建/更新时间

#### VideoSummary (视频摘要表)
- **uuid**: 摘要唯一标识符 (主键)
- **course_uuid**: 关联课程UUID (外键)
- **video_summary**: 视频摘要内容
- **created_at**: 创建时间

#### Report (学习报告表)
- **uuid**: 报告唯一标识符 (主键)
- **course_uuid**: 关联课程UUID (外键)
- **start_time**: 开始时间
- **end_time**: 结束时间
- **duration**: 持续时间
- **segment_topic**: 段落主题
- **key_points**: 关键点列表 (JSON格式)
- **created_at**: 创建时间

#### ReportEmbedding (报告向量表)
- **uuid**: 向量唯一标识符 (主键)
- **vector**: 向量数据 (JSON字符串格式)
- **report_uuid**: 关联报告UUID (外键)
- **created_at**: 创建时间

#### SummaryEmbedding (摘要向量表)
- **uuid**: 向量唯一标识符 (主键)
- **vector**: 向量数据 (JSON字符串格式)
- **video_summary_uuid**: 关联视频摘要UUID (外键)
- **created_at**: 创建时间

### 数据关系
- Course → VideoSummary (一对多)
- Course → Report (一对多)
- VideoSummary → SummaryEmbedding (一对多)
- Report → ReportEmbedding (一对多)

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 8.0+
- Redis (可选，用于缓存)
- Docker & Docker Compose (推荐)

### 部署方式

#### 🐳 方式一：Docker部署（推荐）

**1. 克隆项目**
```bash
git clone [项目地址]
cd resource_recommendation/backend
```

**2. 配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

**3. 一键启动**
```bash
# 使用 Docker Compose 启动所有服务（包含MySQL数据库）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

**4. 验证部署**
```bash
# 检查健康状态
curl http://localhost:8000/health

# 测试课程推荐API
curl "http://localhost:8000/api/v1/recommendation/rag/search/courses?query=机器学习"

# 测试批量处理API
curl -X POST "http://localhost:8000/api/v1/recommendation/rag/process" \
  -H "Content-Type: application/json" \
  -d '[{"course_id":"test-001","resource_name":"测试课程","file_name":"test.mp4","grade":"高中","subject":"信息技术","dialogue":[]}]'

# 访问API文档
open http://localhost:8000/docs
```

#### 🔧 方式二：本地开发部署

**1. 克隆项目**
```bash
git clone [项目地址]
cd resource_recommendation/backend
```

**2. 创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. 安装依赖**
```bash
pip install -r requirements.txt
```

**4. 环境配置**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

**5. 数据库初始化**
```bash
# 创建数据库
mysql -u root -p < sql/init.sql

# 运行迁移
alembic upgrade head
```

**6. 启动服务**
```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🐳 Docker部署详解

### 镜像优化特性
- **轻量级**: 基于Alpine Linux，镜像大小仅~200MB
- **快速构建**: 使用国内镜像源，构建时间缩短至1-2分钟
- **安全**: 非root用户运行，提升容器安全性
- **健康检查**: 内置健康检查机制，确保服务稳定

### 服务架构
```
┌─────────────────┐    ┌─────────────────┐
│   Backend API   │    │     MySQL       │
│   (Port 8000)   │◄──►│   (Port 3306)   │
│   FastAPI       │    │   MySQL 8.0     │
└─────────────────┘    └─────────────────┘
```

### 常用Docker命令

**启动服务**
```bash
# 启动所有服务
docker-compose up -d

# 重新构建并启动
docker-compose up -d --build

# 指定服务启动
docker-compose up -d backend
```

**查看状态**
```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
```

**维护操作**
```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 进入容器
docker-compose exec backend sh

# 查看容器内部文件
docker-compose exec backend ls -la /app/backend/
```

### 故障排查

**构建失败**
- 检查Dockerfile语法
- 确认网络连接正常（国内用户已配置阿里云镜像）
- 查看详细错误日志: `docker-compose logs backend`

**服务启动失败**
- 检查端口占用: `netstat -tulnp | grep 8000`
- 验证数据库连接: `docker-compose exec backend python -c "import mysql.connector"`
- 查看健康检查: `curl http://localhost:8000/health`

### 性能对比

| 指标 | 传统部署 | Docker部署 |
|------|----------|------------|
| 镜像大小 | - | ~200MB |
| 构建时间 | 5-10分钟 | 1-2分钟 |
| 启动时间 | 手动配置 | 30秒 |
| 环境一致性 | 低 | 高 |
| 扩展性 | 复杂 | 简单 |

### 环境变量配置

创建 `.env` 文件，配置以下关键参数：

```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=resource_recommendation
MYSQL_USER=appuser
MYSQL_PASSWORD=your_app_password

# 应用配置
DATABASE_URL=mysql+pymysql://appuser:your_app_password@mysql:3306/resource_recommendation
DEBUG=False
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📖 API文档

### 基础信息
- **文档地址**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json

### 核心API端点

#### 1. 课程语义搜索
```http
GET /api/v1/recommendation/rag/search/courses?query={查询字符串}&top_k={数量}
```

**参数说明**:
- `query`: 搜索关键词（必填）
- `top_k`: 返回结果数量，默认5，最大20

**响应示例**:
```json
{
  "code": 200,
  "msg": "搜索完成",
  "data": [
    {
      "course_uuid": "uuid-string",
      "course_id": "course-001",
      "resource_name": "机器学习基础",
      "file_name": "ml-basics.mp4",
      "grade": "高中",
      "subject": "信息技术",
      "summary": "本课程介绍机器学习的基本概念...",
      "similarity_score": 0.95
    }
  ]
}
```

#### 2. 报告语义搜索
```http
GET /api/v1/recommendation/rag/search/reports/{course_uuid}?query={查询字符串}&top_k={数量}
```

**参数说明**:
- `course_uuid`: 课程UUID（路径参数）
- `query`: 搜索关键词（必填）
- `top_k`: 返回结果数量，默认5，最大20

**响应示例**:
```json
{
  "code": 200,
  "msg": "搜索完成",
  "data": [
    {
      "report_uuid": "uuid-string",
      "start_time": "00:05:30",
      "end_time": "00:15:45",
      "duration": "10:15",
      "segment_topic": "线性回归算法",
      "key_points": ["损失函数", "梯度下降", "参数优化"],
      "similarity_score": 0.92,
      "course_info": {
        "course_uuid": "uuid-string",
        "course_id": "course-001",
        "resource_name": "机器学习基础"
      }
    }
  ]
}
```

#### 3. 批量处理课程数据
```http
POST /api/v1/recommendation/rag/process
```

**请求体**:
```json
[
  {
    "course_id": "course-001",
    "resource_name": "机器学习基础",
    "file_name": "ml-basics.mp4",
    "grade": "高中",
    "subject": "信息技术",
    "video_link": "https://example.com/video.mp4",
    "learning_objectives": "掌握机器学习基本概念和算法",
    "learning_style_preference": "视觉学习",
    "knowledge_level_self_assessment": "初学者",
    "dialogue": [
      {
        "timestamp": "00:00:00",
        "speaker": "老师",
        "text": "今天我们开始学习机器学习"
      },
      {
        "timestamp": "00:01:30",
        "speaker": "老师",
        "text": "机器学习是人工智能的一个重要分支"
      }
    ]
  }
]
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "处理完成",
  "data": {
    "processed_courses": 1,
    "created_summaries": 1,
    "created_reports": 5,
    "created_embeddings": 6
  }
}
```

## 🔧 配置说明

### 环境变量 (.env)
```bash
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:123456@mysql:3306/education_db
DATABASE_URL_SYNC=mysql+pymysql://root:123456@mysql:3306/education_db

# LLM配置 (OpenAI兼容)
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=your-embedding-api-key
EMBEDDING_BASE_URL=https://api.openai.com/v1

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000

# MySQL配置 (Docker环境)
MYSQL_ROOT_PASSWORD=123456
MYSQL_DATABASE=education_db
MYSQL_USER=app_user
MYSQL_PASSWORD=app_password
```

## 📊 数据导入

### 1. 批量导入课程数据
```python
# 使用提供的process_data.py工具
python data/process_data.py --input data/data.json --batch-size 100
```

### 2. 手动添加课程
```python
from backend.app.recommendation.services.rag_service import rag_service

# 准备课程数据
course_data = {
    "course_id": "course-001",
    "resource_name": "课程名称",
    "file_name": "video.mp4",
    "grade": "高中",
    "subject": "数学",
    "dialogue": [...]
}

# 调用处理服务
result = await rag_service.process_course_data([course_data])
```

## 🧪 测试

### 单元测试
```bash
pytest tests/ -v
```

### 集成测试
```bash
pytest tests/integration/ -v
```

### API测试
```bash
# 使用httpie测试
http GET localhost:8000/api/v1/recommendation/rag/search/courses query="机器学习"

# 使用curl测试
curl -X GET "http://localhost:8000/api/v1/recommendation/rag/search/courses?query=机器学习&top_k=5"
```

## 🔍 性能优化

### 1. 数据库优化
- 为常用查询字段添加索引
- 使用连接池优化数据库连接
- 实现查询缓存机制

### 2. 向量计算优化
- 使用近似最近邻搜索（ANN）
- 实现向量缓存机制
- 批量处理优化

### 3. 缓存策略
- Redis缓存热门查询结果
- 向量预计算和缓存
- 数据库查询结果缓存

## 🚨 常见问题

### Q1: 如何处理大量数据的导入？
A: 使用批量处理接口，每批建议100-500条记录，配合异步处理提高效率。

### Q2: 搜索精度不够怎么办？
A: 
- 调整embedding模型参数
- 优化查询预处理
- 增加训练数据量
- 考虑使用更先进的模型

### Q3: 数据库连接超时？
A:
- 检查数据库连接配置
- 增加连接池大小
- 优化查询性能
- 添加重试机制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目主页: [项目地址]

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和教育工作者。

---

**文档更新时间**: 2024年
**版本**: v1.0.0