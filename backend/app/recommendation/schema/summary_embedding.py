from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class SummaryEmbeddingBase(BaseModel):
    vector: List[float] = Field(..., description="向量数据")
    video_summary_uuid: UUID = Field(..., description="关联的视频摘要UUID")

class SummaryEmbeddingCreate(SummaryEmbeddingBase):
    pass

class SummaryEmbeddingResponse(SummaryEmbeddingBase):
    uuid: UUID
    created_at: str

    class Config:
        from_attributes = True