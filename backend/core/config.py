#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # 基础配置
    app_name: str = Field(default="Resource Recommendation API", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")

    # 数据库配置
    mysql_host: str = Field(default="127.0.0.1", description="MySQL主机")
    mysql_port: int = Field(default=3306, description="MySQL端口")
    mysql_user: str = Field(default="root", description="MySQL用户名")
    mysql_password: str = Field(default="12345678", description="MySQL密码")
    mysql_database: str = Field(default="resource_recommendation", description="MySQL数据库名")
    database_url_env: Optional[str] = Field(default=None, description="数据库URL环境变量")

    # 构建完整的数据库URL
    @property
    def database_url(self) -> str:
        # 如果是docker环境，优先使用环境变量中的DATABASE_URL_ENV
        if self.environment == "docker" and self.database_url_env:
            return self.database_url_env
        # 否则使用分开的配置项构建URL
        return f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

    # LLM API配置
    api_key: str = Field(default="", description="OpenAI API密钥")
    base_url: str = Field(default="http://106.227.68.83:8000", description="OpenAI API基础URL")
    model: str = Field(default="qwen2.5-32b", description="OpenAI模型名称")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI模型名称")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="./logs/app.log", description="日志文件路径")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()
