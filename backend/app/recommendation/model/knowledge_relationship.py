#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.recommendation.model.base import uuid4_str

from backend.common.model import Base, id_key


class KnowledgeRelationship(Base):
    __tablename__ = 'knowledge_relationship'

    id: Mapped[id_key] = mapped_column(init=False)
    source_entity_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_entity.uuid'))
    target_entity_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_entity.uuid'))
    knowledge_graph_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_graph.uuid'))
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(Text, comment='关系名称')
    type: Mapped[str] = mapped_column(Text, comment='关系类型')
    attributes: Mapped[str] = mapped_column(Text, comment='关系属性')
    source: Mapped[str] = mapped_column(Text, comment='三元组的源信息')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')
    knowledge_graph: Mapped['KnowledgeGraph'] = relationship('KnowledgeGraph', back_populates='relationships', init=False)
