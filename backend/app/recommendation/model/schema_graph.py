#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.app.recommendation.model.base import uuid4_str
from backend.common.model import Base, id_key


class SchemaGraph(Base):
    __tablename__ = 'schema_graph'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    kg_base_uuid: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Schema Graph Name')
    aim: Mapped[str | None] = mapped_column(Text, default=None, comment='目标描述')
    modify_info: Mapped[str | None] = mapped_column(Text, default=None, comment='修改信息')
    modify_suggestion: Mapped[str | None] = mapped_column(Text, default=None, comment='修改建议')
    text_data: Mapped[str | None] = mapped_column(LONGTEXT, default=None, comment='种子文本')

    entities: Mapped[list['SchemaEntity']] = relationship(
        'SchemaEntity',
        back_populates='schema_graph',
        cascade='all, delete-orphan',
        init=False
    )

    relationships: Mapped[list['SchemaRelationship']] = relationship(
        'SchemaRelationship',
        back_populates='schema_graph',
        cascade='all, delete-orphan',
        init=False
    )

    knowledge_graphs: Mapped[list['KnowledgeGraph']] = relationship(
        "KnowledgeGraph",
        # back_populates="schema_graph",
        cascade="all, delete-orphan",
        init=False,
    )
