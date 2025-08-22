#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from sapperrag.core_setting.path_conf import BasePath


class Settings(BaseSettings):
    """Global Settings"""

    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    # Env Config
    ENVIRONMENT: Literal['dev', 'pro']

    # 从单点门户系统获取用户信息所需URL
    SSO_USER_INFO_URL: str | None = 'http://127.0.0.1:5000/tsp/v1/sys/users/me'  # 不提供则默认本地

    # 索引导出URL
    INDEX_EXPORT_URL_ROOT: str | None = 'http://127.0.0.1:8000/knowg/v1/knowledge/ask'  # 不提供则默认本地

    # Env MySQL
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    # Env Token
    TOKEN_SECRET_KEY: str  # 密钥 secrets.token_urlsafe(32)

    # Env Opera Log
    OPERA_LOG_ENCRYPT_SECRET_KEY: str  # 密钥 os.urandom(32), 需使用 bytes.hex() 方法转换为 str

    # FastAPI
    FASTAPI_API_V1_PATH: str = '/knowg/v1'
    # PATH_FROM_LWR: str = '/lwr'
    FASTAPI_TITLE: str = 'FastAPI'
    FASTAPI_VERSION: str = '0.0.1'
    FASTAPI_DESCRIPTION: str = 'FastAPI Best Architecture'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/docs'
    FASTAPI_REDOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/redocs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_API_V1_PATH}/openapi'
    FASTAPI_STATIC_FILES: bool = True

    @model_validator(mode='before')
    @classmethod
    def validate_openapi_url(cls, values):
        if values['ENVIRONMENT'] == '':
            values['OPENAPI_URL'] = None
        return values

    # MySQL
    MYSQL_ECHO: bool = False
    MYSQL_DATABASE: str = 'onlineunigraph'
    MYSQL_CHARSET: str = 'utf8mb4'

    # Redis
    REDIS_TIMEOUT: int = 5

    # Token
    TOKEN_ALGORITHM: str = 'HS256'  # 算法
    # TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 365  # 过期时间，单位：秒 ？？一年？？
    TOKEN_EXPIRE_SECONDS: int =  120*60  # 过期时间，单位：秒  一小时
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # refresh token 过期时间，单位：秒  一周
    TOKEN_REDIS_PREFIX: str = 'fba:token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'fba:refresh_token'





    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [  # JWT / RBAC 白名单
        f'{FASTAPI_API_V1_PATH}/auth/login',
        f'{FASTAPI_API_V1_PATH}/oauth2/jxnu/jxnu-auth',
        f'{FASTAPI_API_V1_PATH}/auth/captcha',
        f'{FASTAPI_API_V1_PATH}/auth/register',
        f'{FASTAPI_API_V1_PATH}/sys/users/register',
        f'{FASTAPI_API_V1_PATH}/sys/users/reset_password',
        f'{FASTAPI_API_V1_PATH}/show/worklogs/show',
        f'{FASTAPI_API_V1_PATH}/auth/sso',
        f'{FASTAPI_API_V1_PATH}/auth/ssologin',
        f'{FASTAPI_API_V1_PATH}/worklogs/search',
        f'{FASTAPI_API_V1_PATH}/worklogs/ask',
        f'{FASTAPI_API_V1_PATH}/worklogs/search',
        f'{FASTAPI_API_V1_PATH}/worklogs/submit',
        f'{FASTAPI_API_V1_PATH}/worklogs/check_text',
    ]

    # JWT
    JWT_USER_REDIS_PREFIX: str = 'fba:user'
    JWT_USER_REDIS_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7

    # Permission (RBAC)
    # PERMISSION_MODE: Literal['casbin', 'role-menu'] = 'casbin'
    PERMISSION_MODE: Literal['casbin', 'role-menu'] = 'role-menu'
    PERMISSION_REDIS_PREFIX: str = 'fba:permission'

    # RBAC
    # Casbin
    RBAC_CASBIN_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/logout'),
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/token/new'),
    }

    # Role-Menu
    RBAC_ROLE_MENU_EXCLUDE: list[str] = [
        'sys:monitor:redis',
        'sys:monitor:server',
    ]

    # Cookies
    COOKIE_REFRESH_TOKEN_KEY: str = 'fba_refresh_token'
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # Log
    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_LOGURU_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_CID_DEFAULT_VALUE: str = '-'
    LOG_CID_UUID_LENGTH: int = 32  # must <= 32
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_STDOUT_FILENAME: str = 'fba_access.log'
    LOG_STDERR_FILENAME: str = 'fba_error.log'

    # Middleware
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = True

    # Trace ID
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://localhost:5175',
        'http://localhost:5273',
        'http://localhost:5001',
        'http://localhost:8000',
        'https://data.jxselab.com'
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]

    # DateTime
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Request limiter
    REQUEST_LIMITER_REDIS_PREFIX: str = 'fba:limiter'

    # Demo mode (Only GET, OPTIONS requests are allowed)
    DEMO_MODE: bool = False
    DEMO_MODE_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/login'),
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/logout'),
        ('GET', f'{FASTAPI_API_V1_PATH}/auth/captcha'),
    }

    # Ip location
    IP_LOCATION_PARSE: Literal['online', 'offline', 'false'] = 'offline'
    IP_LOCATION_REDIS_PREFIX: str = 'fba:ip:location'
    IP_LOCATION_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # 过期时间，单位：秒

    # Opera log
    OPERA_LOG_PATH_EXCLUDE: list[str] = [
        '/favicon.ico',
        FASTAPI_DOCS_URL,
        FASTAPI_REDOCS_URL,
        FASTAPI_OPENAPI_URL,
        f'{FASTAPI_API_V1_PATH}/auth/login/swagger',
        f'{FASTAPI_API_V1_PATH}/oauth2/github/callback',
        f'{FASTAPI_API_V1_PATH}/oauth2/linux-do/callback',
    ]
    OPERA_LOG_ENCRYPT_TYPE: int = 1  # 0: AES (性能损耗); 1: md5; 2: ItsDangerous; 3: 不加密, others: 替换为 ******
    OPERA_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [  # 将加密接口入参参数对应的值
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]


@lru_cache
def get_settings() -> Settings:
    """获取全局配置"""
    return Settings()


# 创建配置实例
settings = get_settings()
