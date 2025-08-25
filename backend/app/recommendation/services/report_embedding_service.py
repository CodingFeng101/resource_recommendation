from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import json

from ..crud import report_embedding_dao
from ..schema.report_embedding import ReportEmbeddingCreate, ReportEmbeddingResponse

class ReportEmbeddingService:
    def __init__(self, db: Session):
        self.db = db

    def create_report_embedding(self, embedding_data: ReportEmbeddingCreate) -> ReportEmbeddingResponse:
        embedding = report_embedding_dao.create(self.db, obj_in=embedding_data)
        return ReportEmbeddingResponse.from_orm(embedding)

    def get_report_embedding(self, uuid: UUID) -> Optional[ReportEmbeddingResponse]:
        embedding = report_embedding_dao.get(self.db, uuid=uuid)
        if not embedding:
            return None
        
        # 将JSON字符串转换回列表
        response = ReportEmbeddingResponse.from_orm(embedding)
        response.vector = json.loads(embedding.vector)
        return response

    def get_embeddings_by_report(
        self, report_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportEmbeddingResponse]:
        embeddings = report_embedding_dao.get_by_report_uuid(
            self.db, report_uuid=report_uuid, skip=skip, limit=limit
        )
        
        responses = []
        for embedding in embeddings:
            response = ReportEmbeddingResponse.from_orm(embedding)
            response.vector = json.loads(embedding.vector)
            responses.append(response)
        return responses

    def get_all_report_embeddings(self, skip: int = 0, limit: int = 100) -> List[ReportEmbeddingResponse]:
        embeddings = report_embedding_dao.get_multi(self.db, skip=skip, limit=limit)
        
        responses = []
        for embedding in embeddings:
            response = ReportEmbeddingResponse.from_orm(embedding)
            response.vector = json.loads(embedding.vector)
            responses.append(response)
        return responses

    def delete_report_embedding(self, uuid: UUID) -> bool:
        embedding = report_embedding_dao.get(self.db, uuid=uuid)
        if not embedding:
            return False
        report_embedding_dao.remove(self.db, uuid=uuid)
        return True