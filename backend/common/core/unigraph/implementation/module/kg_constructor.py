import json
import os
from typing import List, Dict, Tuple

from backend.common.core.rag.build_index.dialogue_process.dialogue_process import DialogueProcessor
from ..ai_unit.executor.ai_executor import AIExecutor
import asyncio
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class SemanticKGConstructor:
    def __init__(self, kg_schema: List, schema_definition: Dict):
        self.kg_schema = self._convert_schema2old_format(kg_schema)
        # self.kg_schema = kg_schema
        self.schema_definition = schema_definition
        self.ai_executor = AIExecutor()

    @staticmethod
    def _convert_schema2old_format(schema_data):
        """
        将新格式的schema数据转换为旧格式，保持功能不变
        """
        old_schema_data = []
        for type_triple in schema_data:
            try:
                old_schema = type_triple["schema"]
                old_schema_data.append(old_schema)
            except KeyError:
                continue

        return old_schema_data

    async def _process_chunk(self, chunk):
        """
        处理文本块
        """
        result = await self.ai_executor.execute(
            self,
            chunk=chunk,
            kg_schema=self.kg_schema,
            schema_definition=self.schema_definition,
        )
        return result

    async def extract_kg(self, text_data: str) -> Tuple[List, List]:
        """
        提取指定类型文件的KG
        """
        # 将文本字典解包，遍历每个键值对并对值进行类型判断，如果是列表则将其并入当前文本总列表中
        all_chunks = DialogueProcessor.chunk_with_overlap(dialogue=text_data)

        kg = list()
        triple_sources = list()

        # 创建任务列表
        tasks = [self._process_chunk(chunk) for chunk in all_chunks]

        # 使用tqdm创建进度条
        with tqdm(total=len(tasks), desc=f"Processing text chunks count {len(all_chunks)}") as pbar:
            # 使用as_completed实时获取完成的任务
            for completed_task in asyncio.as_completed(tasks):
                triples, triple_source = await completed_task
                if triples:  # 确保非空值被添加进容器中
                    kg.extend(triples)
                if triple_source:
                    triple_sources.extend(triple_source)


        return kg, triple_sources