from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import json

from backend.app.recommendation.model import SummaryEmbedding
from ..schema.summary_embedding import SummaryEmbeddingCreate


class CRUDSummaryEmbedding:
    def create(self, db: Session, *, obj_in: SummaryEmbeddingCreate) -> SummaryEmbedding:
        # 将向量转换为JSON字符串存储
        vector_str = json.dumps(obj_in.vector)
        db_obj = SummaryEmbedding(
            vector=vector_str,
            video_summary_uuid=obj_in.video_summary_uuid
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, uuid: UUID) -> Optional[SummaryEmbedding]:
        stmt = select(SummaryEmbedding).where(SummaryEmbedding.uuid == uuid)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_video_summary_uuid(
        self, db: Session, *, video_summary_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[SummaryEmbedding]:
        stmt = select(SummaryEmbedding).where(
            SummaryEmbedding.video_summary_uuid == video_summary_uuid
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[SummaryEmbedding]:
        stmt = select(SummaryEmbedding).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def remove(self, db: Session, *, uuid: UUID) -> SummaryEmbedding:
        stmt = select(SummaryEmbedding).where(SummaryEmbedding.uuid == uuid)
        result = db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # 异步方法
    async def create_async(self, db: AsyncSession, *, obj_in: SummaryEmbeddingCreate) -> SummaryEmbedding:
        # 将向量转换为JSON字符串存储
        vector_str = json.dumps(obj_in.vector)
        db_obj = SummaryEmbedding(
            vector=vector_str,
            video_summary_uuid=obj_in.video_summary_uuid
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_async(self, db: AsyncSession, *, uuid: UUID) -> Optional[SummaryEmbedding]:
        stmt = select(SummaryEmbedding).where(SummaryEmbedding.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_async(self, db: AsyncSession) -> List[SummaryEmbedding]:
        """获取所有summary_embedding记录"""
        stmt = select(SummaryEmbedding)
        result = await db.execute(stmt)
        return result.scalars().all()

summary_embedding_dao = CRUDSummaryEmbedding()