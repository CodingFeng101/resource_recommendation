#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.common.exception.exception import BaseError
from backend.core.logging import logger
import traceback


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """自定义HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """数据验证异常处理器"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url.path)
        }
    )


async def base_exception_handler(request: Request, exc: BaseError):
    """自定义基础异常处理器"""
    return JSONResponse(
        status_code=exc.code or 500,
        content={
            "error": exc.msg,
            "status_code": exc.code or 500,
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )
