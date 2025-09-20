import numpy as np
import librosa
from scipy.ndimage import gaussian_filter
from . import change_volume  # 从同级目录导入


def process(y, sr, sigma=1.5, wet=1.0, n_fft=1024, hop_length=512, db=0):
    """
    在音频的频谱图上应用高斯模糊，产生平滑的模糊感。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    sigma (float): 高斯模糊的标准差。值越大，声音越模糊。
    wet (float): 干/湿混合比例 (0 到 1)。
    n_fft (int): STFT的窗口大小。
    hop_length (int): STFT的帧移。
    db (float): 对模糊后的声音进行音量调整（分贝）。

    返回:
    np.ndarray: 处理后的音频数据。
    """
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = np.abs(D), np.angle(D)

    blurred_magnitude = gaussian_filter(magnitude, sigma=sigma)

    D_blurred = blurred_magnitude * np.exp(1j * phase)
    y_blur = librosa.istft(D_blurred, hop_length=hop_length, length=len(y))

    if db != 0:
        y_blur = change_volume.process(y_blur, sr, db=db)

    return (1 - wet) * y + wet * y_blur