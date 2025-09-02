import asyncio
import json
from jinja2 import Template

from tqdm import tqdm

from backend.common.clean import clean_json_output
from backend.common.core.llm.response_getter import GenericResponseGetter
from .prompt import REPORT_GENERATION, LABEL_GENERATION


class DialogueProcessor:
    def __init__(self):
        self.llm = GenericResponseGetter()
        self.sem = asyncio.Semaphore(15)

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
                cleaned_report = clean_json_output(report)
                try:
                    return json.loads(cleaned_report)
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
                segment_topic_embedding = await self.llm.get_vector(query=report.get("segment_topic"))
                report["segment_topic_embedding"] = segment_topic_embedding
                return report

        tasks = [process_report(report) for report in report_list]
        result_list = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="report_embedding"):
            result_list.append(await coro)
        return result_list

    async def label_generate(self, report_list):
        segment_topic_list = [report["segment_topic"] for report in report_list]
        template = Template(LABEL_GENERATION)
        agent_query = template.render(segment_topic_list=json.dumps(segment_topic_list))
        label = await self.llm.get_response(query=agent_query)
        return json.loads(clean_json_output(label))

    async def label_embedding(self, label):
        class_summary = label["class_summary"]
        if not class_summary:
            class_summary = "无可用信息"
        summary_embedding = await self.llm.get_vector(query=class_summary)
        label["summary_embedding"] = summary_embedding
        return label

    async def process(self, dialogue: list):
        # 处理数据的逻辑
        dialogue_chunks = self.chunk_with_overlap(dialogue=dialogue)
        report_list = await self.report_generate(chunks=dialogue_chunks)
        report_with_embedding = await self.report_embedding(report_list=report_list)
        label = await self.label_generate(report_list=report_list)
        label_with_embedding = await self.label_embedding(label=label)
        return {"report_with_embedding": report_with_embedding, "label_with_embedding": label_with_embedding}

async def main():
    with open(r"D:\PycharmProjects\resource_recommendation\backend\data\data.txt", "r", encoding="utf-8") as f:
        dialogues = json.load(f)
    processor = DialogueProcessor()
    report = await processor.process(dialogues)
    print(report)

if __name__ == "__main__":
    asyncio.run(main())