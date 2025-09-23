# 场景1：远场交互 (例如，在客厅对智能音箱说话)
# 特点：高混响，低音量

SCENE_CONFIG = {
    # 'scene_name' 将用作 data_output 下的子文件夹名
    "scene_name": "far_field",

    # 效果链
    "effects": [
        {
            "name": "add_reverb",
            "params": {
                "room_size": 0.7,      # 模拟一个较大的房间 (0到1)
                "damping": 0.8,        # 墙壁吸收部分高频，声音更柔和
                "wet_level": 0.6,      # 混响声的比例较高
                "dry_level": 0.4       # 原始直达声的比例较低
            }
        },

        {
            "name": "apply_filter",
            "params": {
                "filter_type": "lowpass",
                # 截止频率设为 4000Hz，会削弱齿音(s, t)的清晰度，但不会让语音无法辨认
                "cutoff_hz": 1000,
                "repeat": 10  # 应用一次即可获得自然的效果
            }
        },

        {
            "name": "change_volume",
            "params": {
                "target_lufs": -50  # 音量降低12分贝，模拟距离衰减
            }
        }
    ]
}