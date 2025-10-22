import os
import dashscope
from http import HTTPStatus

# --- 新增部分：明确指定API服务区域 ---
# 这是官方示例中的配置，用于指定新加坡区的服务。
# 如果您的API Key是在北京区等中国内地创建的，请将其替换为: 'https://dashscope.aliyuncs.com/api/v1'
# dashscope.base_http_api_url = 'https://api.probex.top/v1/chat/completions'


def recognize_local_audio(file_path):
    """
    使用 Qwen3-ASR 模型识别本地音频文件。
    """
    # 1. 检查 API Key 是否已设置
    api_key = "sk-6db6ad89006a45feb8865cc5140a62e2"
    if not api_key:
        print("错误：请先设置环境变量 DASHSCOPE_API_KEY")
        return

    # 2. 自动格式化文件路径
    # 您只需提供标准路径，代码会自动添加 'file://' 前缀
    local_file_path = f"file://{os.path.abspath(file_path)}"
    print(f"正在识别文件: {local_file_path}")
    print(f"使用API服务地址: {dashscope.base_http_api_url}")

    # 3. 构造请求消息
    messages = [
        {
            "role": "system",
            "content": [{"text": ""}]  # 可在此处配置Context以优化特定词汇识别
        },
        {
            "role": "user",
            "content": [
                {"audio": local_file_path},
            ]
        }
    ]

    # 4. 调用 API 并进行健壮的错误处理
    try:
        response = dashscope.MultiModalConversation.call(
            model="qwen3-asr-flash",
            messages=messages,
            api_key=api_key,
            result_format="message",
            asr_options={
                "enable_lid": True,
                "enable_itn": True
            }
        )

        # 5. 清晰地处理和打印结果
        if response.status_code == HTTPStatus.OK:
            print("\n识别成功！")
            # 直接提取并显示识别出的文本
            recognized_text = response.output.choices[0].message.content[0]['text']
            print("识别结果:", recognized_text)
        else:
            print(f"\n识别失败，请求ID: {response.request_id}")
            print(f"状态码: {response.status_code}")
            print(f"错误码: {response.code}")
            print(f"错误信息: {response.message}")

    except Exception as e:
        print(f"\n调用 API 时发生未知异常: {e}")


if __name__ == '__main__':
    # --- 请将这里替换为您本地音频文件的实际路径 ---
    # 例如:
    # - Windows: "D:/audios/my_test_audio.wav"
    # - Linux/macOS: "/home/user/audios/my_test_audio.mp3"
    audio_file_to_recognize = "evalued/far_field/human_1/human_1_variant_1.wav"

    if "ABSOLUTE_PATH" in audio_file_to_recognize:
        print("请在代码中将 'ABSOLUTE_PATH/welcome.mp3' 替换为您本地音频文件的绝对路径！")
    else:
        recognize_local_audio(audio_file_to_recognize)