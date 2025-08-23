from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class ReportEmbedding(Base):
    __tablename__ = 'report_embeddings'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vector = Column(Text, nullable=False)  # 存储向量数据的JSON字符串
    report_uuid = Column(String(36), ForeignKey('reports.uuid'), nullable=False)
    
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    report = relationship("Report", back_populates="report_embeddings")
    
    def __repr__(self):
        return f"<ReportEmbedding(uuid='{self.uuid}', report_uuid='{self.report_uuid}')>"