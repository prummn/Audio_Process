import os
import dashscope
import json
from http import HTTPStatus
import time

# --- 1. API 全局配置 ---

# 强烈建议：将 API Key 设置为环境变量，代码会自动读取
# 如果未设置环境变量，代码会回退到使用下面这个硬编码的 Key
API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-6db6ad89006a45feb8865cc5140a62e2")

# 明确指定API服务区域 (非常重要！)
# 如果您的 API Key 是在国内（如北京、杭州）创建的，请使用下面这行：
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'


# 如果您的 API Key 是在国际区（如新加坡）创建的，请使用下面这行：
# dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'


def recognize_audio_with_api(audio_file_path: str) -> str:
    """
    使用 Qwen3-ASR API 转录单个音频文件。
    成功则返回识别的文本，失败则返回 None。
    """
    # 构造符合 API 要求的文件路径
    local_file_path_for_api = f"file://{os.path.abspath(audio_file_path)}"

    messages = [
        {"role": "system", "content": [{"text": ""}]},
        {"role": "user", "content": [{"audio": local_file_path_for_api}]}
    ]

    try:
        response = dashscope.MultiModalConversation.call(
            model="qwen3-asr-flash",
            messages=messages,
            api_key=API_KEY,
            result_format="message",
            asr_options={"enable_lid": True, "enable_itn": True}
        )

        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0].message.content[0]['text'].strip()
        else:
            print(f"[API_ERROR] 文件 '{audio_file_path}' 转录失败: "
                  f"Code: {response.code}, Message: {response.message}")
            return None

    except Exception as e:
        print(f"[EXCEPTION] 调用 API 时发生异常 for file '{audio_file_path}': {e}")
        return None


def process_directory(root_dir: str):
    """
    遍历给定根目录，对每个二级子目录进行处理，使用 Qwen-ASR API 生成 eval.jsonl。
    """
    print(f"开始批量处理目录: {root_dir}")
    print(f"使用API服务地址: {dashscope.base_http_api_url}")
    if not API_KEY or "sk-xxx" in API_KEY:
        print("\n[警告] 未找到有效的 API Key，请设置 DASHSCOPE_API_KEY 环境变量或在代码中提供。")
        return

    # 遍历每个二级文件夹（每个子文件夹即为一个任务）
    for sub_dir in os.listdir(root_dir):
        sub_dir_path = os.path.join(root_dir, sub_dir)
        if not os.path.isdir(sub_dir_path):
            continue

        eval_file_path = os.path.join(sub_dir_path, 'eval.jsonl')
        is_first_record_in_group = True  # 用于判断是覆盖写入(w)还是追加(a)

        print(f"\n--- 开始处理任务: {sub_dir} ---")

        # 遍历该二级文件夹下的所有三级子文件夹
        for third_level_dir in os.listdir(sub_dir_path):
            third_level_dir_path = os.path.join(sub_dir_path, third_level_dir)

            if os.path.isdir(third_level_dir_path):
                audio_files = [f for f in os.listdir(third_level_dir_path) if f.lower().endswith('.wav')]
                if not audio_files:
                    continue

                print(f"  正在处理子目录: {third_level_dir} ({len(audio_files)} 个文件)")

                # 打开 eval.jsonl 文件以写入或追加
                write_mode = 'w' if is_first_record_in_group else 'a'
                with open(eval_file_path, write_mode, encoding='utf-8') as eval_file:
                    for audio_file in audio_files:
                        audio_file_path = os.path.join(third_level_dir_path, audio_file)

                        # 使用 API 转录音频文件
                        text = recognize_audio_with_api(audio_file_path)

                        # 如果API调用失败，text会是None，我们将其置为空字符串
                        if text is None:
                            text = ""

                        record = {
                            "audio_path": audio_file_path,
                            "response": text,
                            "original_key": third_level_dir
                        }

                        eval_file.write(json.dumps(record, ensure_ascii=False) + "\n")

                        # 成功写入第一个记录后，后续都应使用追加模式
                        is_first_record_in_group = False

                        # API 有调用频率限制，短暂休眠一下可以避免触发流控
                        time.sleep(0.5)

                print(f"  [OK] 完成处理: {third_level_dir_path}")

        print(f"--- 任务 {sub_dir} 完成, 结果已保存至 {eval_file_path} ---")


if __name__ == "__main__":
    # 设置要处理的根目录
    root_dir = "evalued/far_field"

    # 开始批量处理
    process_directory(root_dir)

    print("\n所有任务处理完毕！")