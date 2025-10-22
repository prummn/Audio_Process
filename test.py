import requests
import json

# --- 1. 配置您的信息 ---
API_URL = "https://api.probex.top/v1/chat/completions"
# 请将 "YOUR_API_KEY" 替换为您自己的 Key
API_KEY = "sk-1cC3eEKj3nfn6nn63AbFcFeszXrH12iGwQ4OvcdaOrRfRIua"
MODEL_NAME = "deepseek-v3"

# --- 2. 准备请求头 ---
# 注意 Authorization 的格式通常是 "Bearer " + key
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- 3. 准备请求体 (payload) ---
# 将 stream 设置为 false 以获取完整响应
payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "user",
            "content": "你好，请用一句话介绍一下你自己。"
        }
    ],
    "stream": False
}

# --- 4. 发送 POST 请求 ---
try:
    print("正在向模型发送请求，请稍候...")
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    # 检查请求是否成功
    response.raise_for_status()

    # --- 5. 解析并打印结果 ---
    response_json = response.json()

    # 提取模型返回的内容
    assistant_message = response_json['choices'][0]['message']['content']

    print("\n模型回复:")
    print(assistant_message)

    # 打印完整的返回信息以供调试
    # print("\n--- 完整响应 ---")
    # print(response_json)

except requests.exceptions.RequestException as e:
    print(f"\n请求失败: {e}")
    # 如果有响应内容，也打印出来，方便排查API Key或请求格式问题
    if e.response is not None:
        print(f"响应状态码: {e.response.status_code}")
        print(f"响应内容: {e.response.text}")
