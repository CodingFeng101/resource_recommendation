from __future__ import annotations
from pydantic import model_validator, Field
from backend.common.schema import SchemaBase
from datetime import datetime


class SchemaGraphBase(SchemaBase):
    """获取图谱详情"""
    name: str | None = Field("")
    aim: str | None = Field("")
    kg_base_uuid: str | None = Field("")
    modify_info: str | None = Field("")
    modify_suggestion: str | None = Field("")


class SchemaGraphResponse(SchemaGraphBase):
    id: int
    uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddSchemaGraphParam(SchemaBase):
    file_paths: list[str] | None
    data: SchemaGraphBase


class UpdateSchemaGraphBase(SchemaBase):
    """获取图谱详情"""
    name: str | None = None
    aim: str | None = None
    modify_info: str | None = None
    modify_suggestion: str | None = None


class UpdateSchemaGraphParam(SchemaBase):
    file_paths: list[str] | None
    data: UpdateSchemaGraphBase

class ImportSchemaGraphParam(SchemaBase):
    file_paths: list[str] | None
    data: SchemaGraphBase



