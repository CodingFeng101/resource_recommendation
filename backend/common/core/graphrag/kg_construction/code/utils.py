import pandas as pd


def extract_qa_pairs_xlsx(file_path, sheet_index=0):
    """
    从xlsx文件提取"问题"和"答案"列，组合成问答对元组列表
    使用工作表索引而非名称，避免字典返回问题

    参数:
        file_path: xlsx文件路径
        sheet_index: 工作表索引，默认为0（第一个工作表）

    返回:
        list: 包含(问题, 答案)元组的列表
    """
    try:
        # 直接使用索引读取工作表，确保返回单个DataFrame
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_index,  # 使用索引而非名称
            engine='openpyxl'
        )

        # 再次确认我们得到的是DataFrame
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"预期得到DataFrame，但得到了{type(df)}。请检查文件格式。")

        # 检查列名（忽略大小写和空格）
        columns = [str(col).strip().lower() for col in df.columns]
        required = ['问题', '答案']
        required_lower = [col.lower() for col in required]

        missing = [req for req in required_lower if req not in columns]
        if missing:
            raise ValueError(f"表格缺少必要列：{', '.join([required[required_lower.index(m)] for m in missing])}")

        # 找到对应的列名
        question_col_index = columns.index('问题')
        answer_col_index = columns.index('答案')
        question_col = df.columns[question_col_index]
        answer_col = df.columns[answer_col_index]

        # 提取并组合问答对
        qa_pairs = []
        for index, row in df.iterrows():
            question = row[question_col]
            answer = row[answer_col]

            # 过滤空值
            if pd.notna(question) and pd.notna(answer):
                qa_pairs.append((str(question).strip(), str(answer).strip()))

        return qa_pairs

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在")
        return []
    except IndexError:
        print(f"错误：工作表索引 {sheet_index} 不存在，请检查索引是否正确")
        return []
    except Exception as e:
        print(f"处理文件时出错：{str(e)}")
        return []


# 示例用法
if __name__ == "__main__":
    # 替换为你的xlsx文件路径
    file_path = "小红书运营问答知识库.xlsx"

    # 尝试读取第一个工作表（索引为0）
    qa_list = extract_qa_pairs_xlsx(file_path, sheet_index=0)

    # 如果第一个工作表失败，尝试第二个（索引为1）
    if not qa_list:
        print("尝试读取第二个工作表...")
        qa_list = extract_qa_pairs_xlsx(file_path, sheet_index=1)

    # 显示结果
    if qa_list:
        print(f"成功提取到 {len(qa_list)} 个问答对:")
        for i, (question, answer) in enumerate(qa_list, 1):
            print(f"{i}. 问题: {question}")
            print(f"   答案: {answer}")
            print("-" * 60)
    else:
        print("未能提取到有效的问答对")
