# stutter
# 特点：背景噪音与目标语音频谱相似，且每次处理的噪音文件都可能不同

SCENE_CONFIG = {
    "scene_name": "stutter",  # 可以改个名字以示区别

    "effects": [
        {
            "name": "apply_filter",
            "params": {
                "filter_type": "lowpass",
                # 截止频率设为 4000Hz，会削弱齿音(s, t)的清晰度，但不会让语音无法辨认
                "cutoff_hz": {"random_type": "uniform", "min": 1000, "max": 1500, "is_core": True},
                "repeat": {"random_type": "randint", "min": 2, "max": 3}  # 应用一次即可获得自然的效果
            }
        },
        {
            "name": "add_stutter_replace",
            "params": {
                "stutter_prob": {"random_type": "uniform", "min": 0.35, "max": 0.4, "is_core": True},
                "repeat_prob": {"random_type": "uniform", "min": 0.5, "max": 0.7, },
                "max_repeats": {"random_type": "randint", "min": 2, "max": 3, },

            }
        }


        # {
        #     "name": "adjust_speed",
        #     "params": {
        #         "speed_factor": {"random_type": "uniform", "min": 0.95, "max": 1.05}  # 轻微调整语速，增加多样性
        #     }
        # }
    ]

}