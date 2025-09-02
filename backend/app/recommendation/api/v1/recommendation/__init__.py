from fastapi import APIRouter
from backend.app.recommendation.api.v1.recommendation.rag import router as rag_router
from backend.app.recommendation.api.v1.recommendation.unigraph import router as unigraph_router

router = APIRouter(prefix='/recommendation', tags=['Recommendation'])

router.include_router(rag_router, prefix='/rag', tags=['RAG'])
router.include_router(unigraph_router, prefix='/implementation', tags=['UNIGRAPH'])
