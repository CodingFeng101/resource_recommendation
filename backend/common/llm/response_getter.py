from openai import AsyncOpenAI
from backend.common.llm.base import ResponseGetter
from backend.core.config import settings


class GenericResponseGetter(ResponseGetter):
    @staticmethod
    async def get_response(
            query: str,
            api_key: str = settings.api_key,
            base_url: str = settings.base_url,
            model: str = settings.model
    ) -> str:
        """
        聊天式API接口
        :param api_key: API密钥
        :param base_url: API地址
        :param query: 查询内容
        :param model: 模型名称
        :return: 返回结果
        """
        async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        completion = await async_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是对话概括专家。"
                },
                {
                    "role": "user",
                    "content": query
                },
            ],
            temperature=0
        )
        return completion.choices[0].message.content

    @staticmethod
    async def get_vector(
            query: str,
            api_key: str = settings.api_key,
            base_url: str = settings.base_url,
            model: str = settings.embedding_model
    ) -> list[float]:
        """
        向量嵌入API接口
        :param query: 查询内容
        :param model: 模型名称
        :param api_key: API密钥
        :param base_url: API地址
        """
        async_embedding_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        completion = await async_embedding_client.embeddings.create(
            model=model,
            input=[query]
        )
        return completion.data[0].embedding

