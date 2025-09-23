# 场景2：鸡尾酒会 (从'human_voice'类别中随机选取噪音)
# 特点：背景噪音与目标语音频谱相似，且每次处理的噪音文件都可能不同

SCENE_CONFIG = {
    "scene_name": "cocktail_party_random",  # 可以改个名字以示区别

    "effects": [
        {
            "name": "add_reverb",
            "params": {
                "room_size": 0.4,
                "damping": 0.8,        # 墙壁吸收部分高频，声音更柔和
                "wet_level": 0.4,      # 混响声的比例较高
                "dry_level": 0.6       # 原始直达声的比例较低
            }
        },
        {
            "name": "change_volume",
            "params": {
                "target_lufs": -30  # 音量降低12分贝，模拟距离衰减
            }
        },
        {
            "name": "add_noise",
            "params": {
                # 使用新参数指定噪音类别文件夹
                "noise_category": "human_voice",

                # 噪声只比信号低 10dB，非常嘈杂
                "noise_db": 5
            }
        }
    ]
}