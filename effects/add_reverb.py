from pedalboard import Pedalboard, Reverb


def process(y, sr, room_size=0.6, damping=0.5, wet_level=0.3, dry_level=0.7):
    """
    使用 pedalboard 添加高质量的混响效果。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    room_size (float): 模拟的房间大小 (0 到 1)。值越大，空间感越强。
    damping (float): 混响的阻尼 (0 到 1)。控制高频的衰减速度，值越大衰减越快。
    wet_level (float): 湿信号（混响声）的音量比例 (0 到 1)。
    dry_level (float): 干信号（原始声）的音量比例 (0 到 1)。

    返回:
    np.ndarray: 添加混响后的音频数据。
    """
    board = Pedalboard([
        Reverb(room_size=room_size, damping=damping, wet_level=wet_level, dry_level=dry_level)
    ])
    return board(y, sr)