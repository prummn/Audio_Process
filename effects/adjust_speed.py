import os
import random
import librosa
import soundfile as sf
import numpy as np

def process(y, sr, speed_min=0.5, speed_max=2.0):
    """
    以随机速率改变音频的播放速度。
    采用 librosa 的 time-stretch 实现，不会改变音高。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    speed_min (float): 随机速度的下限。
    speed_max (float): 随机速度的上限。

    返回:
    tuple[np.ndarray, float]:
        - np.ndarray: 改变速度后的音频数据。
        - float: 本次随机采用的实际速度值。
    """
    speed = random.uniform(speed_min, speed_max)
    # librosa.effects.time_stretch 需要短时傅里叶变换
    y_stretched = librosa.effects.time_stretch(y, rate=speed)
    return y_stretched.astype(np.float32)