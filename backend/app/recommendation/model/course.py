#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from backend.app.recommendation.model.base import uuid4_str
from backend.common.model import MappedBase as Base


class Course(Base):
    """课程表"""
    __tablename__ = 'courses'
    
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    course_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    resource_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    video_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    learning_objectives: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    learning_style_preference: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    knowledge_level_self_assessment: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    dialogue: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    video_summaries: Mapped[list['VideoSummary']] = relationship(
        "VideoSummary", 
        back_populates="course", 
        cascade="all, delete-orphan"
    )
    knowledge_graphs: Mapped[list['KnowledgeGraph']] = relationship(
        "KnowledgeGraph",
        back_populates="courses",
        cascade="all, delete-orphan"
    )
    reports: Mapped[list['Report']] = relationship(
        "Report",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Course(course_id='{self.course_id}', resource_name='{self.resource_name}')>"