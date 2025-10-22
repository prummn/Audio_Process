# 大空间强混响 (例如，在客厅对智能音箱说话)
# 特点：高混响，低音量

SCENE_CONFIG = {
    # 'scene_name' 将用作 data_output 下的子文件夹名
    "scene_name": "strong_echo",

    # 效果链
    "effects": [
        {
            "name": "add_reverb",
            "params": {
                "room_size": {"random_type": "uniform", "min": 0.75, "max": 0.85, "is_core": True},      # 模拟一个较大的房间 (0到1)
                "damping": {"random_type": "uniform", "min": 0.6, "max": 0.7},        # 墙壁吸收部分高频，声音更柔和
                "wet_level": {"random_type": "uniform", "min": 0.6, "max": 0.7},      # 混响声的比例较高
                "dry_level": {"random_type": "uniform", "min": 0.5, "max": 0.6}      # 原始直达声的比例较6
            }
        },

        {
            "name": "apply_filter",
            "params": {
                "filter_type": "lowpass",
                # 截止频率设为 4000Hz，会削弱齿音(s, t)的清晰度，但不会让语音无法辨认
                "cutoff_hz": {"random_type": "uniform", "min": 1000, "max": 3000, "is_core": True},
                "repeat": {"random_type": "randint", "min": 2, "max": 10}  # 应用一次即可获得自然的效果
            }
        },

        {
            "name": "add_echo",
            "params": {
                "delay_seconds": {"random_type": "uniform", "min": 0.1, "max": 0.3, "is_core": True},  # 回声延迟时间
                "feedback": {"random_type": "uniform", "min": 0.5, "max": 0.7, },       # 回声反馈量
                "mix": {"random_type": "uniform", "min": 0.2, "max": 0.4, }             # 回声音量（
            }
        },

        {
            "name": "change_volume",
            "params": {
                "target_lufs": {"random_type": "uniform", "min": -40, "max": -25, "is_core": True}  # 音量降低12分贝，模拟距离衰减
            }
        },
        # {
        #     "name": "adjust_speed",
        # }
    ]

}