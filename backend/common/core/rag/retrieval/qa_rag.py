import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.common.llm.response_getter import GenericResponseGetter
from backend.common.core.rag.retrieval.base import RAG


class IntelligentQARAG(RAG):
    def __init__(self):
        self.llm = GenericResponseGetter()

    async def query_embedding(self, query: str):
        query_embedding = await self.llm.get_vector(query=query)
        return np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    async def retrieve(self, query_embedding: np.ndarray, report_with_embedding: list, top_k=10):
        """
        根据查询向量从 report_with_embedding 中检索最相似的 top_k 报告
        :param query_embedding: (1, D) 形状的查询向量
        :param report_with_embedding: 每个元素是包含 'segment_topic_embedding' 的字典
        :param top_k: 返回的报告数量
        """
        similarities = []

        for report in report_with_embedding:
            segment_topic_embedding = report.get("segment_topic_embedding")
            segment_topic_embedding = np.array(segment_topic_embedding, dtype=np.float32).reshape(1, -1)

            # 计算余弦相似度
            similarity = float(cosine_similarity(query_embedding, segment_topic_embedding))
            similarities.append((report, similarity))

        # 相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 只返回 report（如果需要相似度可以返回 similarities[:top_k]）
        return [report for report, _ in similarities[:top_k]]
