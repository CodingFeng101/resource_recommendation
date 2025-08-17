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
│       │   └── v1/
│       │       └── recommendation/
│       ├── crud/             # 数据访问层
│       ├── model/            # 数据库模型
│       ├── schema/           # 数据验证schema
│       └── services/         # 业务逻辑层
├── common/                   # 公共组件
├── core/                     # 核心配置
├── database/                 # 数据库配置
└── data/                     # 数据处理工具
```

## 📋 数据模型

### 核心实体
- **Course**: 课程基本信息
- **VideoSummary**: 视频摘要信息
- **Report**: 学习报告详情
- **ReportEmbedding**: 报告的向量表示
- **SummaryEmbedding**: 摘要的向量表示

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 8.0+
- Redis (可选，用于缓存)

### 安装步骤

1. **克隆项目**
```bash
git clone [项目地址]
cd resource_recommendation/backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **环境配置**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

5. **数据库初始化**
```bash
# 创建数据库
mysql -u root -p < sql/init.sql

# 运行迁移
alembic upgrade head
```

6. **启动服务**
```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
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
GET /api/v1/recommendation/rag/search/reports/{course_id}?query={查询字符串}&top_k={数量}
```

**参数说明**:
- `course_id`: 课程ID（路径参数）
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
    "dialogue": [
      {
        "timestamp": "00:00:00",
        "speaker": "老师",
        "text": "今天我们开始学习机器学习"
      }
    ]
  }
]
```

## 🔧 配置说明

### 环境变量 (.env)
```bash
# 数据库配置
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/education_db

# LLM配置
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
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