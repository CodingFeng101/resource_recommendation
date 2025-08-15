from abc import abstractmethod, ABC


class RAG(ABC):
    @abstractmethod
    async def query_embedding(self, query: str):
        """将用户查询转为向量"""
        pass

    @abstractmethod
    async def retrieve(self, query_embedding, report_with_embedding, top_k: int = 10):
        """根据查询向量检索相关文档或节点"""
        pass