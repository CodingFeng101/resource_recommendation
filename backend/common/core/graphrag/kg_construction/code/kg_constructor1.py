from openai import OpenAI
from dotenv import load_dotenv
import json
from jinja2 import Template
from kg_construction.code.utils import extract_qa_pairs_xlsx
import os
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import threading
import itertools

# 加载 .env 文件中的环境变量
load_dotenv()

# 从 .env 读取 API key 列表
# .env 示例： api_key_list=["sk-xxx","sk-yyy","sk-zzz"]
api_key_list_str = os.getenv("API_KEY_LIST", "[]")
try:
    api_key_list = json.loads(api_key_list_str)
    if not isinstance(api_key_list, list) or not api_key_list:
        raise ValueError("api_key_list 必须是一个非空列表")
except Exception as e:
    raise ValueError(f"api_key_list 格式错误，请在 .env 中确保其为 JSON 列表: {e}")

# 创建线程安全的 API Key 轮询器
_key_lock = threading.Lock()
_key_cycle = itertools.cycle(api_key_list)

def get_next_client():
    """线程安全地获取下一个 API Key 对应的 OpenAI 客户端"""
    with _key_lock:
        key = next(_key_cycle)
    return OpenAI(api_key=key)

# 读取prompt模板（全局读取一次，避免重复IO）
def load_prompt_template():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    prompt_path = os.path.join(script_dir, "../prompt/prompt.txt")
    prompt_path = os.path.normpath(prompt_path)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return Template(f.read())

# 加载prompt模板
prompt_template = load_prompt_template()

def get_completion(prompt, model="gpt-5"):
    messages = [{"role": "user", 'content': prompt}]
    client = get_next_client()  # 每次调用使用不同的 key
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )
    try:
        content = response.choices[0].message.content
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0].strip()
            return json.loads(json_str)
        return json.loads(content)
    except json.JSONDecodeError:
        return content

def extract_list(data):
    """检查数据结构，提取列表"""
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                return value
        return []
    elif isinstance(data, list):
        return data
    else:
        return []

def process_single_qa(qa_pair, index, model, prompt_template):
    """处理单个问答对的函数，用于并行执行"""
    question, answer = qa_pair
    QA = f"{index}. 问题: {question}     答案: {answer}"

    while True:  # 循环直到获取到非空的 triples
        prompt = prompt_template.render(QA=QA)
        triples = get_completion(prompt, model)
        triples = extract_list(triples)
        if triples:
            break

    return [{"triple": triple, "source": QA} for triple in triples]

def extract_triples_from_xlsx(file_path, model="gpt-5", max_workers=100):
    """
    从Excel提取三元组，支持并行处理
    """
    qa_list = extract_qa_pairs_xlsx(file_path, sheet_index=0)
    all_triples = []
    total = len(qa_list)

    process_func = functools.partial(
        process_single_qa,
        model=model,
        prompt_template=prompt_template
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_func, qa_pair, i + 1): i
            for i, qa_pair in enumerate(qa_list)
        }
        for future in tqdm.tqdm(
                as_completed(futures),
                total=total,
                desc="处理进度"
        ):
            try:
                result = future.result()
                all_triples.extend(result)
            except Exception as e:
                index = futures[future]
                print(f"处理第{index + 1}个问答对时出错: {str(e)}")

    return all_triples

if __name__ == "__main__":
    result = extract_triples_from_xlsx("小红书运营问答知识库.xlsx", max_workers=5)
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
