import asyncio
import json
from jinja2 import Template

from tqdm import tqdm

from backend.common.llm.response_getter import GenericResponseGetter
from report_generation_prompt import REPORT_GENERATION

class DialogueProcessor:
    def __init__(self):
        self.llm = GenericResponseGetter()
        self.sem = asyncio.Semaphore(20)

    @staticmethod
    def chunk_with_overlap(dialogue, chunk_size=20, overlap=5):
        step = chunk_size - overlap
        return [dialogue[i:i + chunk_size] for i in range(0, len(dialogue), step)]

    async def report_generate(self, chunks: list):
        async def process_chunk(chunk):
            async with self.sem:
                template = Template(REPORT_GENERATION)
                agent_query = template.render(dialogue_data=json.dumps(chunk))
                report = await self.llm.get_response(query=agent_query)
                try:
                    return json.loads(report)
                except json.JSONDecodeError:
                    return {}

        tasks = [process_chunk(chunk) for chunk in chunks]
        report_list = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="report_generate"):
            report_list.append(await coro)
        return report_list

    async def report_embedding(self, report_list: list):
        async def process_report(report):
            async with self.sem:
                duration_embedding = await self.llm.get_vector(query=report.get("duration"))
                report["duration_embedding"] = duration_embedding
                return report

        tasks = [process_report(report) for report in report_list]
        result_list = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="report_embedding"):
            result_list.append(await coro)
        return result_list

    async def process(self, dialogue: list):
        # 处理数据的逻辑
        dialogue_chunks = self.chunk_with_overlap(dialogue=dialogue)
        report_list = await self.report_generate(chunks=dialogue_chunks)
        report_with_embedding = await self.report_embedding(report_list=report_list)
        return report_with_embedding

