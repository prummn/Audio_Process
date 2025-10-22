import os
import whisper
import torch
import json

def process_directory(root_dir: str, model: whisper.Whisper):
    """
    遍历给定根目录（root_dir），对每个二级子目录（对应不同的音频组）进行处理，生成 eval.jsonl。
    
    参数：
        root_dir: 包含音频的根目录。
        model: Whisper 模型，用于音频转录。
    """
    count_sub=0
    # 遍历每个二级文件夹（每个子文件夹即为一个任务）
    for sub_dir in os.listdir(root_dir):
        sub_dir_path = os.path.join(root_dir, sub_dir)
        # 构建 eval.jsonl 文件路径，保存到二级文件夹下
        eval_file_path = os.path.join(sub_dir_path, 'eval.jsonl')
        count=0
        # 确保这是一个文件夹
        if os.path.isdir(sub_dir_path):
            # 获取该二级文件夹下的所有三级子文件夹
            for third_level_dir in os.listdir(sub_dir_path):
                third_level_dir_path = os.path.join(sub_dir_path, third_level_dir)
                
                # 确保是三级子文件夹，且包含音频文件
                if os.path.isdir(third_level_dir_path):
                    audio_files = [f for f in os.listdir(third_level_dir_path) if f.lower().endswith('.wav')]
                    if audio_files:

                        # 打开 eval.jsonl 文件以写入
                        write_mode = 'w' if count==0 else 'a'
                        count+=1
                        with open(eval_file_path, write_mode, encoding='utf-8') as eval_file:
                            for audio_file in audio_files:
                                audio_file_path = os.path.join(third_level_dir_path, audio_file)
                                
                                # 转录音频文件
                                try:
                                    result = model.transcribe(audio_file_path)
                                    text = result.get('text', '').strip()
                                except Exception as e:
                                    print(f"[ERROR] 转录失败: {audio_file_path} -> {e}")
                                    text = ""
                                
                                # 生成 JSON 记录
                                record = {
                                    "audio_path": audio_file_path,
                                    "response": text,
                                    "original_key": third_level_dir  # 这里的 original_key 就是三级文件夹名
                                }

                                # 写入一行 JSON 数据
                                eval_file.write(json.dumps(record, ensure_ascii=False) + "\n")

                        print(f"[OK] 处理完成: {third_level_dir_path}")


if __name__ == "__main__":
    # 自动选择设备：有 GPU 就用 GPU，否则用 CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # 加载 Whisper 模型
    model = whisper.load_model("turbo", device=device)

    # 根目录
    root_dir = "data_output/"

    # 批量处理
    process_directory(root_dir, model)
