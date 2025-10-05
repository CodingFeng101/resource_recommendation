#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from backend.core.config import settings
from backend.core.logging import logger
from backend.database.db_mysql import create_table
from backend.app.recommendation.api.router import api_router
from backend.common.exception.exception_handlers import (
    custom_http_exception_handler,
    validation_exception_handler,
    base_exception_handler,
    general_exception_handler
)
from backend.common.exception.exception import BaseError

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")

    # 创建数据库表
    try:
        await create_table()
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")

    # 创建上传目录
    import os
    if not os.path.exists("backend/uploads"):
        os.makedirs("backend/uploads")
        logger.info(f"创建上传目录: ./uploads")

    # 创建日志目录
    if not os.path.exists("backend/logs"):
        os.makedirs("backend/logs")
        logger.info(f"创建日志目录: ./logs")

    logger.info("应用启动完成")
    yield

    # 关闭时执行
    logger.info("应用关闭中...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="智能资源推荐系统API",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # 添加自定义中间件
    # app.add_middleware(RequestIDMiddleware)
    # app.add_middleware(LoggingMiddleware)
    # app.add_middleware(ErrorHandlerMiddleware)

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 添加可信主机中间件
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.host]
        )

    # 注册异常处理器
    app.add_exception_handler(HTTPException, custom_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BaseError, base_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 注册路由
    app.include_router(api_router, prefix="/api")

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app_version}

    # API文档重定向
    @app.get("/")
    async def root():
        return {"message": "Resource Recommendation API", "docs": "/docs"}

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
