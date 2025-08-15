from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Embedding(Base):
    __tablename__ = 'embeddings'

    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_topic_uuid = Column(CHAR(36), ForeignKey('reports.uuid'), nullable=False)
    vector = Column(Text, nullable=False)  # 存储向量数据，使用Text类型存储JSON格式的向量
    created_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 定义与Report的关系
    report = relationship("Report", back_populates="embedding")

    def __repr__(self):
        return f"<Embedding(uuid='{self.uuid}', segment_topic_uuid='{self.segment_topic_uuid}', created_time='{self.created_time}')>"
