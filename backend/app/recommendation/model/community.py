#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.recommendation.model.base import uuid4_str
from backend.app.recommendation.model.map.community_entity_map import community_entity_map
from backend.common.model import Base, id_key


class Community(Base):
    __tablename__ = 'community'

    id: Mapped[id_key] = mapped_column(init=False)
    knowledge_graph_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_graph.uuid'))
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    title: Mapped[str] = mapped_column(Text, comment='标题')
    level: Mapped[str] = mapped_column(Text, comment='等级')
    content: Mapped[str] = mapped_column(Text, comment='内容')
    rating: Mapped[str] = mapped_column(Text, comment='评分')
    attributes: Mapped[str] = mapped_column(Text, comment='属性')

    knowledge_graph: Mapped['KnowledgeGraph'] = relationship('KnowledgeGraph', back_populates='communities', init=False)

    entities: Mapped[list['KnowledgeEntity']] = relationship('KnowledgeEntity', secondary=community_entity_map,
                                                             back_populates='communities', init=False)
