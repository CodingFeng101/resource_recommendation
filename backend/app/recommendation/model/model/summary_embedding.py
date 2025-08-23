from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class SummaryEmbedding(Base):
    __tablename__ = 'summary_embeddings'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vector = Column(Text, nullable=False)  # 存储向量数据的JSON字符串
    video_summary_uuid = Column(String(36), ForeignKey('video_summaries.uuid'), nullable=False)
    
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    video_summary = relationship("VideoSummary", back_populates="summary_embeddings")
    
    def __repr__(self):
        return f"<SummaryEmbedding(uuid='{self.uuid}', video_summary_uuid='{self.video_summary_uuid}')>"