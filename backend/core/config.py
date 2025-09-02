#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from functools import lru_cache
from typing import Optional, List, Union, Literal

from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类"""

    # 基础配置
    app_name: str = Field(description="应用名称")
    app_version: str = Field(description="应用版本")
    debug: bool = Field(description="调试模式")
    environment: str = Field(description="运行环境")

    # 服务器配置
    host: str = Field(description="服务器地址")
    port: int = Field(description="服务器端口")

    # MySQL 数据库配置
    MYSQL_HOST: str = Field(description="MySQL主机")
    MYSQL_PORT: int = Field(description="MySQL端口")
    MYSQL_USER: str = Field(description="MySQL用户名")
    MYSQL_PASSWORD: str = Field(description="MySQL密码")
    MYSQL_DATABASE: str = Field(description="MySQL数据库名")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="./logs/app.log", description="日志文件路径")

    # DateTime
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    @model_validator(mode='before')
    @classmethod
    def validate_openapi_url(cls, values):
        """验证 OpenAPI URL"""
        if values.get('ENVIRONMENT') == 'pro':
            values['FASTAPI_OPENAPI_URL'] = None
        return values

    # 构建完整的数据库URL
    @property
    def database_url(self) -> str:
        """
        构建数据库连接URL
        
        :return: 数据库连接URL
        """
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


