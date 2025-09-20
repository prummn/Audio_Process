import numpy as np
from pydub import AudioSegment


def process(y, sr, filter_type='lowpass', cutoff_hz=1000, repeat=1, wet=1.0):
    """
    使用 pydub 应用一个或多个高通或低通滤波器。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    filter_type (str): 滤波器类型。可选 'lowpass' 或 'highpass'。
    cutoff_hz (int): 滤波器的截止频率（Hz）。
                     对于 'lowpass'，高于此频率的声音将被衰减。
                     对于 'highpass'，低于此频率的声音将被衰减。
    repeat (int): 应用滤波器的次数。次数越多，效果越强。
    wet (float): 干/湿混合比例 (0 到 1)。

    返回:
    np.ndarray: 处理后的音频数据。
    """
    # 将 numpy 数组转换为 pydub 的 AudioSegment
    audio = AudioSegment(
        (y * 32767).astype(np.int16).tobytes(),
        frame_rate=sr, sample_width=2, channels=1
    )

    for _ in range(repeat):
        if filter_type == 'lowpass':
            audio = audio.low_pass_filter(cutoff_hz)
        elif filter_type == 'highpass':
            audio = audio.high_pass_filter(cutoff_hz)
        else:
            # 如果提供了无效的 filter_type，则引发错误
            raise ValueError("filter_type 必须是 'lowpass' 或 'highpass'")

    y_filtered = np.array(audio.get_array_of_samples()).astype(np.float32) / 32767.0

    min_len = min(len(y), len(y_filtered))
    y, y_filtered = y[:min_len], y_filtered[:min_len]

    return (1 - wet) * y + wet * y_filtered
