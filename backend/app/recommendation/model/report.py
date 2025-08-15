from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Report(Base):
    __tablename__ = 'reports'
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(String(50), nullable=False)
    end_time = Column(String(50), nullable=False)
    duration = Column(String(50), nullable=False)
    segment_topic = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False)
    
    # 定义与Embedding的关系
    embedding = relationship("Embedding", back_populates="report", uselist=False)

    def __repr__(self):
        return f"<Report(uuid='{self.uuid}', duration='{self.duration}')>"
