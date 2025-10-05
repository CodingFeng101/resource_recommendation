# Cython 编译加密使用指南

本项目支持使用 Cython 对核心代码进行编译加密，提高代码安全性和执行效率。

## 文件说明

- `setup.py` - Cython 编译配置文件
- `compile.py` - 编译脚本工具
- `Dockerfile.compile` - 编译专用 Docker 文件
- `docker-compose.compile.yml` - 编译和部署的 Docker Compose 配置

## 编译的模块

以下核心模块将被编译为 `.so` 文件：

### 核心业务模块
- `app/knowledge_graph/` - 知识图谱相关功能
- `app/admin/` - 管理员功能
- `app/user/` - 用户管理功能

### 通用模块
- `common/response/` - 响应处理
- `common/exception/` - 异常处理
- `common/log.py` - 日志系统
- `core/config.py` - 配置管理
- `database/` - 数据库操作
- `utils/` - 工具函数

## 使用方法

### 方法一：使用编译脚本（推荐）

1. **安装编译依赖**
   ```bash
   pip install Cython numpy setuptools wheel
   ```

2. **运行编译脚本**
   ```bash
   # 基本编译
   python compile.py
   
   # 编译并删除源代码文件
   python compile.py --remove-source
   ```

3. **编译完成后的文件结构**
   ```
   backend/
   ├── dist/                    # wheel 分发包
   ├── build/                   # 编译临时文件
   ├── app/
   │   ├── __init__.py
   │   ├── knowledge_graph/
   │   │   ├── __init__.py
   │   │   ├── service.cpython-311-win_amd64.so  # 编译后的文件
   │   │   └── ...
   │   └── ...
   ├── main.py                  # 入口文件（保留）
   └── ...
   ```

### 方法二：使用 Docker 编译

1. **仅编译**
   ```bash
   docker-compose -f docker-compose.compile.yml run --rm compiler
   ```

2. **编译并运行**
   ```bash
   docker-compose -f docker-compose.compile.yml up app-compiled
   ```

3. **完整部署（包含数据库和缓存）**
   ```bash
   docker-compose -f docker-compose.compile.yml up -d
   ```

### 方法三：手动编译

1. **构建扩展**
   ```bash
   python setup.py build_ext --inplace
   ```

2. **创建分发包**
   ```bash
   python setup.py bdist_wheel
   ```

3. **安装编译后的包**
   ```bash
   pip install dist/*.whl
   ```

## 编译配置

### setup.py 配置说明

- **编译模块**: 在 `MODULES_TO_COMPILE` 中定义需要编译的模块
- **排除文件**: 在 `EXCLUDE_FILES` 中定义不需要编译的文件
- **编译选项**: 可以调整 `compiler_directives` 优化编译结果

### 自定义编译选项

```python
# 在 setup.py 中修改编译选项
compiler_directives = {
    'language_level': 3,
    'boundscheck': False,      # 禁用边界检查（提高性能）
    'wraparound': False,       # 禁用负索引（提高性能）
    'initializedcheck': False, # 禁用初始化检查（提高性能）
    'cdivision': True,         # 使用 C 除法（提高性能）
    'embedsignature': True,    # 嵌入函数签名（便于调试）
}
```

## 部署说明

### 生产环境部署

1. **使用编译后的 Docker 镜像**
   ```bash
   docker build -f Dockerfile.compile -t resource-recommendation:compiled .
   docker run -p 8000:8000 resource-recommendation:compiled
   ```

2. **使用 Docker Compose**
   ```bash
   # 生产环境（包含 Nginx）
   docker-compose -f docker-compose.compile.yml --profile production up -d
   ```

### 环境变量配置

编译后的应用需要以下环境变量：

```bash
# 应用配置
APP_NAME=Resource Recommendation API
ENVIRONMENT=production
DEBUG=false

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=resource_recommendation

# API 配置
API_KEY=your_openai_api_key
BASE_URL=https://api.openai.com/v1
MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

## 性能优化

### 编译优化选项

1. **禁用调试信息**
   ```python
   compiler_directives['boundscheck'] = False
   compiler_directives['wraparound'] = False
   ```

2. **启用 C 优化**
   ```python
   compiler_directives['cdivision'] = True
   compiler_directives['initializedcheck'] = False
   ```

### 运行时优化

1. **使用多进程**
   ```bash
   uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

2. **启用 JIT 编译**（如果使用 NumPy）
   ```bash
   export NUMBA_CACHE_DIR=/tmp/numba_cache
   ```

## 故障排除

### 常见问题

1. **编译失败**
   - 检查是否安装了 C 编译器（Windows 需要 Visual Studio Build Tools）
   - 确保 Python 开发头文件已安装
   - 检查 Cython 版本兼容性

2. **导入错误**
   - 确保 `__init__.py` 文件存在
   - 检查模块路径是否正确
   - 验证编译后的 `.so` 文件权限

3. **性能问题**
   - 检查是否正确设置了编译优化选项
   - 确认使用了合适的 Python 版本
   - 监控内存使用情况

### 调试技巧

1. **保留调试信息**
   ```python
   compiler_directives['embedsignature'] = True
   compiler_directives['linetrace'] = True
   ```

2. **生成 C 代码**
   ```bash
   python setup.py build_ext --inplace --debug
   ```

3. **查看编译日志**
   ```bash
   python compile.py 2>&1 | tee compile.log
   ```

## 安全注意事项

1. **源代码保护**: 编译后可以选择删除源代码文件
2. **密钥管理**: 确保 API 密钥等敏感信息通过环境变量传递
3. **访问控制**: 限制对编译后文件的访问权限
4. **版本控制**: 不要将编译后的 `.so` 文件提交到版本控制系统

## 许可证

编译后的代码仍然遵循原项目的许可证条款。