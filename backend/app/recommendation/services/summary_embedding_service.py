from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import json

from ..crud import summary_embedding_dao
from ..schema.summary_embedding import SummaryEmbeddingCreate, SummaryEmbeddingResponse

class SummaryEmbeddingService:
    def __init__(self, db: Session):
        self.db = db

    def create_summary_embedding(self, embedding_data: SummaryEmbeddingCreate) -> SummaryEmbeddingResponse:
        embedding = summary_embedding_dao.create(self.db, obj_in=embedding_data)
        return SummaryEmbeddingResponse.from_orm(embedding)

    def get_summary_embedding(self, uuid: UUID) -> Optional[SummaryEmbeddingResponse]:
        embedding = summary_embedding_dao.get(self.db, uuid=uuid)
        if not embedding:
            return None
        
        # 将JSON字符串转换回列表
        response = SummaryEmbeddingResponse.from_orm(embedding)
        response.vector = json.loads(embedding.vector)
        return response

    def get_embeddings_by_video_summary(
        self, video_summary_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[SummaryEmbeddingResponse]:
        embeddings = summary_embedding_dao.get_by_video_summary_uuid(
            self.db, video_summary_uuid=video_summary_uuid, skip=skip, limit=limit
        )
        
        responses = []
        for embedding in embeddings:
            response = SummaryEmbeddingResponse.from_orm(embedding)
            response.vector = json.loads(embedding.vector)
            responses.append(response)
        return responses

    def get_all_summary_embeddings(self, skip: int = 0, limit: int = 100) -> List[SummaryEmbeddingResponse]:
        embeddings = summary_embedding_dao.get_multi(self.db, skip=skip, limit=limit)
        
        responses = []
        for embedding in embeddings:
            response = SummaryEmbeddingResponse.from_orm(embedding)
            response.vector = json.loads(embedding.vector)
            responses.append(response)
        return responses

    def delete_summary_embedding(self, uuid: UUID) -> bool:
        embedding = summary_embedding_dao.get(self.db, uuid=uuid)
        if not embedding:
            return False
        summary_embedding_dao.remove(self.db, uuid=uuid)
        return True