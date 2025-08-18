import logging

import numpy as np
from tqdm.asyncio import tqdm_asyncio
import asyncio

from sapperrag.ai_unit.llm.response_getter import GenericResponseGetter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttributeEmbedder:
    def __init__(self, max_concurrent=100):
        self.semaphore = asyncio.Semaphore(max_concurrent)  # 控制并发量

    @staticmethod
    async def embed_attributes(text_embeder, attributes, api_key, base_url):
        """
        带指数退避重试的嵌入方法

        :param text_embeder: 文本嵌入器
        :param attributes: 实体的属性字典
        :return: 嵌入向量
        """
        max_retries = 3
        backoff_factor = 1

        for attempt in range(max_retries):
            try:
                attributes_text = " ".join(f"{k}: {v}" for k, v in attributes.items())
                response = await text_embeder.get_vector(query=attributes_text,
                                                         api_key="sk-CRj8WW9b6iNIsqqcB5F7Ce9d7e1c431b8e29Ea634aAa4e87",
                                                         base_url="https://api.rcouyi.com/v1")
                logger.info(f"嵌入成功: {attributes_text}")
                return np.array(response)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"嵌入失败: {str(e)}")
                    raise
                await asyncio.sleep(backoff_factor * (2 ** attempt))
        return np.array([])

    async def _process_single_entity(self, index, entity, embeder, api_key, base_url):
        """
        处理单个实体的异步任务

        :param index: 实体的索引
        :param entity: 实体对象
        :return: 实体索引和可能的错误
        """
        async with self.semaphore:  # 控制并发量
            try:
                # 创建属性副本避免修改原始数据
                attributes = entity.attributes.copy()
                attributes["name"] = entity.name

                # 获取嵌入向量
                vector = await AttributeEmbedder.embed_attributes(embeder, attributes, api_key, base_url)

                # 更新实体数据
                entity.attributes_embedding = vector.tolist()
                return index, None
            except Exception as e:
                return index, e
            finally:
                del attributes["name"]

    async def add_attribute_vectors(self, entities, api_key, base_url):
        """
        并发处理所有实体

        :param entities: 实体列表
        :return: 处理后的实体列表
        """
        # 创建任务列表
        embeder = GenericResponseGetter()
        tasks = [
            self._process_single_entity(idx, entity, embeder, api_key, base_url)
            for idx, entity in enumerate(entities)
        ]

        # 使用带进度条的并发执行
        progress_bar = tqdm_asyncio.as_completed(tasks, desc="嵌入实体")

        for future in progress_bar:
            index, error = await future
            if error:
                logger.error(f"处理实体 {index} 时出错: {str(error)}")

        return entities