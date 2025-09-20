from pedalboard import Pedalboard, Delay


def process(y, sr, delay_seconds=0.2, feedback=0.5, mix=0.5):
    """
    使用 pedalboard 添加回声（延迟）效果。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    delay_seconds (float): 回声的延迟时间（秒）。
    feedback (float): 反馈值 (0 到 1)。控制回声的重复次数。
    mix (float): 干/湿信号混合比例 (0 到 1)。0为纯原声, 1为纯回声。

    返回:
    np.ndarray: 添加回声后的音频数据。
    """
    board = Pedalboard([
        Delay(delay_seconds=delay_seconds, feedback=feedback, mix=mix)
    ])
    return board(y, sr)