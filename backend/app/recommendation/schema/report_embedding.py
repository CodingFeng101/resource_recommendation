from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ReportEmbeddingBase(BaseModel):
    vector: List[float] = Field(..., description="向量数据")
    report_uuid: UUID = Field(..., description="关联的报告UUID")

class ReportEmbeddingCreate(ReportEmbeddingBase):
    pass

class ReportEmbeddingResponse(ReportEmbeddingBase):
    uuid: UUID
    created_at: str

    class Config:
        from_attributes = True