from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..model.embedding import Embedding
from ..schema.embedding import EmbeddingCreate, EmbeddingUpdate

class CRUDEmbedding:
    async def create(self, db: AsyncSession, obj_in: EmbeddingCreate) -> Embedding:
        """创建embedding"""
        db_obj = Embedding(
            segment_topic_uuid=obj_in.segment_topic_uuid,
            vector=obj_in.vector
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: str) -> Optional[Embedding]:
        """根据UUID获取embedding"""
        result = await db.execute(select(Embedding).where(Embedding.uuid == id))
        return result.scalar_one_or_none()

    async def get_by_report_uuid(self, db: AsyncSession, report_uuid: str) -> Optional[Embedding]:
        """根据report UUID获取embedding"""
        result = await db.execute(select(Embedding).where(Embedding.segment_topic_uuid == report_uuid))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> List[Embedding]:
        """获取所有embedding"""
        result = await db.execute(select(Embedding))
        return result.scalars().all()

    async def update(self, db: AsyncSession, db_obj: Embedding, obj_in: EmbeddingUpdate) -> Embedding:
        """更新embedding"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> Optional[Embedding]:
        """删除embedding"""
        result = await db.execute(select(Embedding).where(Embedding.uuid == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

embedding = CRUDEmbedding()