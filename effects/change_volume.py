import numpy as np
import pyloudnorm as pyln


def process(y, sr, target_lufs=-23.0):
    """
    【新版本】将音频的响度归一化到指定的目标 LUFS 值。
    LUFS (Loudness Units Full Scale) 是一个更符合人耳感知响度的标准。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    target_lufs (float): 目标响度，单位为 LUFS。
                         - 值越大，声音听起来越响。
                         - -14 LUFS: 适用于音乐流媒体 (如 Spotify, YouTube)。
                         - -23 LUFS: 广播电视响度标准 (EBU R128)。
                         - -28 LUFS: 较安静的背景音。
                         - 默认值为 -23.0。

    返回:
    np.ndarray: 经过响度归一化处理后的音频数据。
    """
    # 1. 创建一个响度计，使用 EBU R128 标准
    meter = pyln.Meter(sr)

    # 2. 测量输入音频的综合响度 (Integrated Loudness)
    try:
        # pyloudnorm 要求输入是 float 类型
        loudness = meter.integrated_loudness(y.astype(np.float32))
    except ValueError:
        # 如果音频太短或几乎为静音，测量可能会失败
        # 在这种情况下，我们选择不改变音量，直接返回原音频
        print(f"⚠️ 警告 (change_volume): 无法测量音频响度 (可能音频过短或为静音)，跳过响度归一化。")
        return y

    # 3. 使用 pyloudnorm 的归一化函数调整音频响度
    y_normalized = pyln.normalize.loudness(y, loudness, target_lufs)

    return y_normalized