# 场景2：鸡尾酒会 (从'human_voice'类别中随机选取噪音)
# 特点：背景噪音与目标语音频谱相似，且每次处理的噪音文件都可能不同

SCENE_CONFIG = {
    "scene_name": "cocktail_party",  # 可以改个名字以示区别

    "effects": [
        {
            "name": "add_reverb",
            "params": {
                "room_size": {"random_type": "uniform", "min": 0.3, "max": 0.6, "is_core": True},   # 模拟中等大小的房间
                "damping": 0.8,        # 墙壁吸收部分高频，声音更柔和
                "wet_level": {"random_type": "uniform", "min": 0.4, "max": 0.6},      # 混响声的比例较高
                "dry_level": {"random_type": "uniform", "min": 0.4, "max": 0.6}       # 原始直达声的比例较低
            }
        },
        {
            "name": "change_volume",
            "params": {
                "target_lufs": {"random_type": "uniform", "min": -30, "max": -15, "is_core": True}  # 音量降低10到30分贝，模拟距离衰减
            }
        },
        {
            "name": "add_noise",
            "params": {
                # 使用新参数指定噪音类别文件夹
                "noise_category": "human_voice",

                # 噪声只比信号低 10dB，非常嘈杂
                "noise_db": {"random_type": "uniform", "min": -10, "max": 10, "is_core": True}
            }
        },
        # {
        #     "name": "adjust_speed",
        #     "params": {
        #         "speed_factor": {"random_type": "uniform", "min": 0.95, "max": 1.05}  # 轻微调整语速，增加多样性
        #     }
        # }
    ]

}