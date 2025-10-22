import json
import os
from typing import Dict
import re


def normalize_text(text: str) -> str:
    """
    对文本进行标准化处理，以便进行WER计算。
    1. 转换为小写。
    2. 移除所有标点符号和特殊字符。
    3. （可选）处理多余的空格。
    """
    # 转换为小写
    text = text.lower()

    # 移除中英文标点符号
    # 这个正则表达式涵盖了大部分中英文标点
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~，。！？；：（）—·《》“”‘’…"""
    text = re.sub(f"[{re.escape(punctuation)}]", "", text)

    # 将多个连续空格替换为单个空格
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# 计算WER（Word Error Rate）等评价指标的函数
def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    计算 Word Error Rate (WER)
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    # 动态规划计算编辑距离
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    
    for i in range(len(ref_words) + 1):
        for j in range(len(hyp_words) + 1):
            if i == 0:
                d[i][j] = j
            elif j == 0:
                d[i][j] = i
            else:
                cost = 0 if ref_words[i-1] == hyp_words[j-1] else 1
                d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)

    wer = d[len(ref_words)][len(hyp_words)] / len(ref_words)
    return wer

# 增加truth字段到eval.jsonl的函数
def add_truth_to_eval(eval_file_path: str, truth_file_path: str) -> None:
    """
    根据eval.jsonl和truth.jsonl中相同的"original_key"，在eval.jsonl增加一个truth字段。
    
    参数：
        eval_file_path: eval.jsonl的路径
        truth_file_path: truth.jsonl的路径
    """
    # 读取truth.jsonl为字典
    truth_data = {}
    with open(truth_file_path, 'r', encoding='utf-8') as f_truth:
        for line in f_truth:
            truth_record = json.loads(line.strip())
            original_key = truth_record["original_key"]
            truth_data[original_key] = truth_record["response"]
    
    # 打开eval.jsonl文件并更新
    updated_eval_data = []
    missing_truth_count = 0  # 统计未能成功标记truth的数量
    with open(eval_file_path, 'r', encoding='utf-8') as f_eval:
        for line in f_eval:
            eval_record = json.loads(line.strip())
            original_key = eval_record["original_key"]
            
            # 查找对应的truth并加入truth字段
            if original_key in truth_data:
                eval_record["truth"] = truth_data[original_key]
            else:
                eval_record["truth"] = ""  # 若没有找到对应的truth, 设置为空
                missing_truth_count += 1  # 未成功标记truth，计数加1
            
            updated_eval_data.append(eval_record)
    
    # 将更新后的数据写回eval.jsonl
    with open(eval_file_path, 'w', encoding='utf-8') as f_eval:
        for record in updated_eval_data:
            f_eval.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"[OK] 添加 truth 字段完成, 更新了 {len(updated_eval_data)} 条记录。")
    print(f"[INFO] 没有成功标记 truth 的记录数: {missing_truth_count}")

# 计算评估指标
def evaluate_asr_metrics(eval_file_path: str) -> Dict[str, float]:
    """
    计算 eval.jsonl 中的 ASR 评估指标（WER 等）。
    """
    wer_total = 0
    num_records = 0
    missing_wer_count = 0

    with open(eval_file_path, 'r', encoding='utf-8') as f_eval:
        for line in f_eval:
            eval_record = json.loads(line.strip())

            # 先进行标准化处理


            response = eval_record.get("response", "")
            truth = eval_record.get("truth", "")

            response = normalize_text(response)
            truth = normalize_text(truth)

            if truth and response:
                wer = calculate_wer(truth, response)
                wer_total += wer
                num_records += 1
            else:
                missing_wer_count += 1

    avg_wer = wer_total / num_records if num_records > 0 else 0.0

    print(f"[INFO] 没有成功计算WER的记录数: {missing_wer_count}")

    return {
        "avg_wer": avg_wer,
        "total_records": num_records
    }

if __name__ == "__main__":
    # 文件路径
    eval_file_path = "../data_composer_evalued/noise_with_barrier/eval.jsonl"
    truth_file_path = "truth.jsonl"
    
    # 添加truth字段到eval.jsonl
    add_truth_to_eval(eval_file_path, truth_file_path)
    
    # 评估ASR指标
    metrics = evaluate_asr_metrics(eval_file_path)
    print(f"评估结果: {metrics}")
