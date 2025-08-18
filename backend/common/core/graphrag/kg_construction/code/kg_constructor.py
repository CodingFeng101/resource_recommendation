from openai import OpenAI
from dotenv import load_dotenv
import json
from jinja2 import Template
from kg_construction.code.utils import extract_qa_pairs_xlsx
import os
import tqdm

# 加载 .env 文件中的环境变量
load_dotenv()

client = OpenAI()


def get_completion(prompt, model="gpt-5"):
    messages = [
        {
            "role": "user",
            'content': prompt
        }]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}  # 这个参数确保返回JSON
    )

    # 尝试解析返回的内容为JSON
    try:
        content = response.choices[0].message.content
        # 如果返回的内容包含代码块，提取JSON部分
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0].strip()
            return json.loads(json_str)
        # 否则直接解析
        return json.loads(content)
    except json.JSONDecodeError:
        # 如果解析失败，返回原始内容
        return content


def extract_list(data):
    """
    检查数据结构，若最外层是字典则尝试提取其中的列表，否则直接返回原数据

    参数:
        data.txt: 待检查的数据（可能是字典、列表或其他类型）

    返回:
        提取到的列表或原数据
    """
    # 检查是否为字典
    if isinstance(data, dict):
        # 尝试提取第一个列表类型的值
        for value in data.values():
            if isinstance(value, list):
                return value
        # 如果字典中没有列表，返回空列表或根据需求处理
        return []
    # 如果本身就是列表，直接返回
    elif isinstance(data, list):
        return data
    # 其他类型返回空列表或根据需求处理
    else:
        return []


def extract_triples_from_xlsx(file_path, model):
    qa_list = extract_qa_pairs_xlsx(file_path, sheet_index=0)
    all_triples = []
    total = len(qa_list)  # 获取总数量

    # 使用tqdm创建进度条，遍历qa_list
    for i, (question, answer) in enumerate(tqdm.tqdm(qa_list, total=total, desc="处理进度"), 1):
        QA = f"{i}. 问题: {question}     答案: {answer}"
        # 获取当前脚本（script.py）的绝对路径
        script_path = os.path.abspath(__file__)  # __file__ 是当前脚本的路径
        # 获取脚本所在目录（code/）
        script_dir = os.path.dirname(script_path)
        # 拼接 prompt.txt 的路径（从 code/ 上一级找 prompt/）
        prompt_path = os.path.join(script_dir, "../prompt/prompt.txt")
        # 规范化路径（自动处理 ../ 等符号，避免路径错误）
        prompt_path = os.path.normpath(prompt_path)
        prompt_template = open(prompt_path, "r", encoding="utf-8").read()
        prompt_template = Template(prompt_template)

        # 循环直到获取到非空的triples
        while True:
            prompt = prompt_template.render(QA=QA)
            triples = get_completion(prompt, model)
            triples = extract_list(triples)

            if triples:  # 如果triples非空则退出循环
                break

        # 处理获取到的有效triples
        triples_with_source = []
        for triple in triples:
            triples_with_source.append({"triple": triple, "source": QA})
        all_triples.extend(triples_with_source)
    return all_triples

if __name__ == "__main__":
    result = extract_triples_from_xlsx("小红书运营问答知识库.xlsx")
    with open("output.json.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)