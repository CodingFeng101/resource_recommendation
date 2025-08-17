import logging

from fastapi import APIRouter

from backend.app.recommendation.api.v1.recommendation.rag_api import rag_router

router = APIRouter(prefix='/recommendation', tags=['Recommendation'])

router.include_router(rag_router, prefix='/rag', tags=['RAG'])