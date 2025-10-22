# import whisper

# # 加载模型到 CPU
# model = whisper.load_model("turbo", device="cpu")

# # 转录音频
# result = model.transcribe(
#     "/mnt/hdd/human_1_blur.wav"
# )

# # 打印转写结果
# print(result["text"])

# # 获取详细信息
# for segment in result["segments"]:
#     print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")



import os
import whisper

# 加载模型到 CPU
model = whisper.load_model("turbo", device="cpu")

# 输入目录
input_dir = "data_evalued/music_background_ambient"

# 遍历目录下所有文件
for filename in os.listdir(input_dir):
    filepath = os.path.join(input_dir, filename)
    # 只处理音频文件（常见格式）
    if not filename.lower().endswith((".wav", ".m4a", ".mp3", ".flac", ".ogg")):
        continue

    try:
        # 转录音频
        result = model.transcribe(filepath, fp16=False)  # CPU 推理要加 fp16=False
        # 打印结果
        print(f"{filename}: {result['text']}")
    except Exception as e:
        print(f"处理 {filename} 出错: {e}")


# import os
# import whisper

# # 加载模型到 CPU（推荐至少用 small/medium 来提升中文效果）
# model = whisper.load_model("medium", device="cpu")

# # 输入目录（中文音频所在文件夹）
# input_dir = "/mnt/hdd/Data/Jialin/datasets--zh-liu799--passsss/wav/part0/1/try/no_noise_wav/zh"

# # 遍历目录下所有文件
# for filename in os.listdir(input_dir):
#     filepath = os.path.join(input_dir, filename)
#     # 只处理音频文件
#     if not filename.lower().endswith((".wav", ".m4a", ".mp3", ".flac", ".ogg")):
#         continue

#     try:
#         # 转录音频，指定中文
#         result = model.transcribe(filepath, fp16=False, language="zh")
#         print(f"{filename}: {result['text']}")
#     except Exception as e:
#         print(f"处理 {filename} 出错: {e}")
