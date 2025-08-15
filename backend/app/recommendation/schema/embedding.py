from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EmbeddingBase(BaseModel):
    segment_topic_uuid: str = Field(..., description="关联的report UUID")
    vector: str = Field(..., description="segment_topic的向量数据，JSON格式字符串")

class EmbeddingCreate(EmbeddingBase):
    pass

class EmbeddingUpdate(BaseModel):
    segment_topic_uuid: Optional[str] = Field(None, description="关联的report UUID")
    vector: Optional[str] = Field(None, description="segment_topic的向量数据，JSON格式字符串")

class Embedding(EmbeddingBase):
    uuid: str = Field(..., description="唯一标识符")
    created_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True