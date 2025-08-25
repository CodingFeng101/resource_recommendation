import re


def clean_json_output(report: str):
    # 去掉 ```json ... ``` 或 ``` ... ```
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", report.strip())
    cleaned = re.sub(r"\n?```$", "", cleaned.strip())
    return cleaned