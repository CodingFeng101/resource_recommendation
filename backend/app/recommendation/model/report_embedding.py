#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid

from backend.common.model import MappedBase as Base

class ReportEmbedding(Base):
    """学习报告向量表"""
    __tablename__ = 'report_embeddings'
    
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vector: Mapped[str] = mapped_column(Text, nullable=False)  # 存储向量数据的JSON字符串
    report_uuid: Mapped[str] = mapped_column(String(36), ForeignKey('reports.uuid'), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    report: Mapped['Report'] = relationship("Report", back_populates="report_embeddings")
    
    def __repr__(self):
        return f"<ReportEmbedding(uuid='{self.uuid}', report_uuid='{self.report_uuid}')>"