#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid

from backend.common.model import MappedBase as Base

class SummaryEmbedding(Base):
    """摘要向量表"""
    __tablename__ = 'summary_embeddings'
    
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vector: Mapped[str] = mapped_column(Text, nullable=False, comment='存储向量数据的JSON字符串')
    video_summary_uuid: Mapped[str] = mapped_column(String(36), ForeignKey('video_summaries.uuid'), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    video_summary: Mapped['VideoSummary'] = relationship("VideoSummary", back_populates="summary_embeddings")
    
    def __repr__(self):
        return f"<SummaryEmbedding(uuid='{self.uuid}', video_summary_uuid='{self.video_summary_uuid}')>"