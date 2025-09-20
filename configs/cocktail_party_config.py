# 场景2：鸡尾酒会 (从'human_voice'类别中随机选取噪音)
# 特点：背景噪音与目标语音频谱相似，且每次处理的噪音文件都可能不同

SCENE_CONFIG = {
    "scene_name": "cocktail_party_random",  # 可以改个名字以示区别

    "effects": [
        {
            "name": "add_noise",
            "params": {
                # 使用新参数指定噪音类别文件夹
                "noise_category": "human_voice",

                # 噪声只比信号低 10dB，非常嘈杂
                "noise_db": -10
            }
        }
    ]
}