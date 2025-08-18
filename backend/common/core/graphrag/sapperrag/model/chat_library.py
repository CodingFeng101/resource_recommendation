from typing import Dict, List

from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import id_key, Base
from backend.database.db_mysql import uuid4_str


class ChatLibrary(Base):
    """聊天消息表"""

    __tablename__ = 'chat_library'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Chat Message Name')
    kg_base_uuid: Mapped[str] = mapped_column(ForeignKey('kg_base.uuid'), nullable=False)
    messages: Mapped[List[Dict[str, str]]] = mapped_column(
            JSON, nullable=True, default_factory=dict
        )

