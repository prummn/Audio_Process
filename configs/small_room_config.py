# 场景5：小空间反射干扰 (模拟在浴室内说话或唱歌)
# 特点：短时混响 (空洞感) + 高频轻微衰减 (沉闷感)

SCENE_CONFIG = {
    "scene_name": "small_space",

    "effects": [
        # 1. 模拟小而反射性强的空间
        {
            "name": "add_reverb",
            "params": {
                # room_size: 设为很小的值 (0.1-0.3) 来模拟浴室、厨房等小空间
                "room_size": 0.1,

                # damping: 设为较低的值，模拟瓷砖、玻璃等硬质表面的高反射性
                "damping": 0.2,

                # wet_level: 适度提高，让混响效果变得明显，形成空洞感
                "wet_level": 0.2,

                # dry_level: 保持原始声音的清晰度
                "dry_level": 0.8
            }
        },

        # 2. 模拟高频被轻微吸收的效果
        {
            "name": "apply_filter",
            "params": {
                "filter_type": "lowpass",
                # 截止频率设在 6000Hz 左右，可以削弱刺耳的高频，但保留了大部分语音清晰度
                "cutoff_hz": 4000
            }
        }
    ]
}
