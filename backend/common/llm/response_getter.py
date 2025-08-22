import asyncio
import json
from typing import List

import aiohttp
from backend.common.llm.base import ResponseGetter


class GenericResponseGetter(ResponseGetter):
    @staticmethod
    async def get_response(
            query: str,
            api_key: str = "",
            base_url: str = "http://106.227.68.83:8000",
            model: str = "qwen2.5-32b"
    ) -> str:
        """
        聊天式API接口
        :param api_key: API密钥
        :param base_url: API基础地址
        :param query: 查询内容
        :param model: 模型名称
        :return: 返回结果
        """
        # 构造请求的URL
        url = f"{base_url.rstrip('/')}/v1/chat/completions"

        # 构造请求的头部
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 构造请求的负载
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是对话概括专家。"
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0
        }
        # 发送POST请求
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
                # 检查响应状态码
                if response.status == 200:
                    # 解析响应内容
                    response_data = await response.json()
                    return response_data['choices'][0]['message']['content']
                else:
                    # 如果响应状态码不是200，抛出异常
                    response_text = await response.text()
                    raise Exception(f"API请求失败，状态码：{response.status}, 响应内容：{response_text}")

    @staticmethod
    async def get_vector(
            query: str,
            base_url: str = "http://106.227.68.83:9997",
            model: str = "bge-large-zh-v1.5"
    ) -> List[float]:
        """
        通过 Ollama 获取句向量
        :param query: 要嵌入的文本
        :param base_url: Ollama 服务地址
        :param model: 模型名称（已在 Ollama 中 pull 过）
        :return: 向量 List[float]
        """
        url = f"{base_url.rstrip('/')}/v1/embeddings"
        payload = {"model": model, "input": query}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload)
            ) as resp:
                if resp.status != 200:
                    raise Exception(
                        f"Ollama 请求失败，状态码：{resp.status}，内容：{await resp.text()}"
                    )
                data = await resp.json()
                # Ollama 返回 {"embedding": [...]}
                return data["data"][0]["embedding"]

# async def main():
#     query = "香蕉"
#     embedding_llm = GenericResponseGetter()
#     vector = await embedding_llm.get_vector(query)
#     print(vector)
#
# if __name__ == "__main__":
#     asyncio.run(main())
