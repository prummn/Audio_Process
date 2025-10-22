# 场景6A：环境音乐背景 (模拟咖啡馆、餐厅)
# 特点：经过滤波的、响度较低的背景音乐 + 统一的房间混响

SCENE_CONFIG = {
    "scene_name": "music_background",
    "metadata": {
        "scene_type": "base"  # 关键字段
    },
    "effects": [
        # 步骤1: 先对主语音应用高通和低通滤波器，模拟它被一个中频设备录制
        # 这一步是可选的，但能增加真实感
        # {
        #     "name": "apply_filter",
        #     "params": {"filter_type": "highpass", "cutoff_hz": 150} # 去除低频嗡嗡声
        # },
        # {
        #     "name": "apply_filter",
        #     "params": {"filter_type": "lowpass", "cutoff_hz": 7000} # 去除刺耳高频
        # },

        {
            "name": "change_volume",
            "params": {
                "target_lufs": {"random_type": "uniform", "min": -45, "max": -30, "is_core": True}  # 音量降低12分贝，模拟距离衰减
            }
        },

        # 步骤2: 添加随机选择的背景音乐
        {
            "name": "add_noise",
            "params": {
                # 假设你有一个名为 'music' 的噪音类别
                "noise_category": "music",
                # 响度设置得较低，确保是“背景”音乐
                "noise_db": {"random_type": "uniform", "min": -10, "max": 0, "is_core": True}
            }
        },

        # 步骤3: 为整体混合声添加统一的、轻微的房间混响
        {
            "name": "add_reverb",
            "params": {
                "room_size": {"random_type": "uniform", "min": 0.4, "max": 0.7, "is_core": True},   # 模拟中等大小的咖啡馆
                "damping": {"random_type": "uniform", "min": 0.4, "max": 0.6},
                "wet_level": 0.3,   # 混响非常轻微，避免声音模糊
                "dry_level": 0.7
            }
        },
        # {
        #     "name": "adjust_speed",
        # }
    ]
}