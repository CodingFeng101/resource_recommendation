# Docker 部署指南

## 快速开始

### 1. 环境准备
确保已安装：
- Docker Engine 20.10+
- Docker Compose 2.0+

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.docker .env

# 编辑配置文件，修改必要的环境变量
nano .env
```

### 3. 构建并启动服务
```bash
# 构建镜像并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 4. 访问服务
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- MySQL: localhost:3306
- Redis: localhost:6379

## 常用命令

### 服务管理
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]
```

### 数据库操作
```bash
# 进入MySQL容器
docker-compose exec mysql mysql -u root -p

# 执行SQL脚本
docker-compose exec mysql mysql -u root -p resource_recommendation < sql/init.sql
```

### 数据持久化
数据会保存在Docker卷中：
- MySQL数据: `mysql_data`
- Redis数据: `redis_data`

### 清理数据
```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（谨慎操作）
docker volume rm backend_mysql_data backend_redis_data
```

## 生产环境部署

### 1. 修改配置
编辑 `docker-compose.yml`：
- 修改密码为强密码
- 关闭端口映射
- 使用外部网络

### 2. 使用环境变量
```bash
# 生产环境配置
export MYSQL_ROOT_PASSWORD=your-strong-password
export MYSQL_PASSWORD=your-app-password
```

### 3. 使用外部数据库
```yaml
# 在docker-compose.yml中注释掉mysql服务
# 修改backend的环境变量指向外部数据库
```

## 故障排除

### 端口冲突
如果端口被占用，修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "3307:3306"  # MySQL使用3307
  - "8001:8000"  # 后端使用8001
```

### 权限问题
```bash
# 修复文件权限
sudo chown -R $USER:$USER .
```

### 镜像构建失败
```bash
# 清理构建缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

## 性能优化

### 资源限制
在 `docker-compose.yml` 中添加资源限制：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 日志管理
```bash
# 设置日志大小限制
docker-compose logs --tail=1000 backend
```