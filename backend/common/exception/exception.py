#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class BaseError(Exception):
    """基础异常类"""
    def __init__(self, msg: str = None, code: int = None):
        self.msg = msg
        self.code = code
        super().__init__(self.msg)


class NotFoundError(BaseError):
    """资源不存在异常"""
    def __init__(self, msg: str = "资源不存在", code: int = 404):
        super().__init__(msg, code)


class ValidationError(BaseError):
    """数据验证异常"""
    def __init__(self, msg: str = "数据验证失败", code: int = 400):
        super().__init__(msg, code)


class DuplicateError(BaseError):
    """重复数据异常"""
    def __init__(self, msg: str = "数据已存在", code: int = 409):
        super().__init__(msg, code)


class DatabaseError(BaseError):
    """数据库操作异常"""
    def __init__(self, msg: str = "数据库操作失败", code: int = 500):
        super().__init__(msg, code)


# 创建一个errors对象来统一管理异常
class Errors:
    NotFoundError = NotFoundError
    ValidationError = ValidationError
    DuplicateError = DuplicateError
    DatabaseError = DatabaseError


errors = Errors()
