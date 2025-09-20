import numpy as np
import librosa
import soundfile as sf
import os
import random


def process(y, sr, use_white_noise=False, noise_category=None, noise_file=None, noise_db=-20, wet=1.0, **kwargs):
    """
    给音频添加背景噪声，支持从特定类别中随机选择噪音文件。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    use_white_noise (bool): 是否使用白噪音。如果 `noise_category` 或 `noise_file` 被指定，此项会被忽略。
    noise_category (str, optional): 噪音类别的文件夹名 (例如 'human_voice')。
                                    如果提供此参数，将从此文件夹中随机选择一个噪音文件。
    noise_file (str, optional): 单个噪音文件的名称。仅在 `noise_category` 未提供时使用。
    noise_db (float): 噪声相对于信号的响度（dB）。
    wet (float): 噪声的混合比例 (0 到 1)。
    kwargs (dict): 用于接收来自主脚本的额外参数，如此处的 'noise_dir'。

    返回:
    np.ndarray: 添加噪声后的音频数据。
    """
    noise_path = None

    # 获取主噪音目录
    noise_dir = kwargs.get("noise_dir", "noises")

    if noise_category:
        category_path = os.path.join(noise_dir, noise_category)
        if not os.path.isdir(category_path):
            print(f"⚠️ 警告 (add_noise): 找不到噪音类别目录 '{category_path}'，跳过此效果。")
            return y

        # 从类别目录中随机选择一个 .wav 文件
        available_noises = [f for f in os.listdir(category_path) if f.lower().endswith('.wav')]
        if not available_noises:
            print(f"⚠️ 警告 (add_noise): 类别目录 '{category_path}' 中没有找到 .wav 文件，跳过此效果。")
            return y

        selected_noise_file = random.choice(available_noises)
        noise_path = os.path.join(category_path, selected_noise_file)
        print(f"  - 随机选择噪音: {os.path.join(noise_category, selected_noise_file)}")

    elif noise_file:
        # 向后兼容，如果只指定了单个文件
        noise_path = os.path.join(noise_dir, noise_file)

    elif use_white_noise:
        # 使用白噪音
        noise = np.random.randn(len(y))
        noise_path = None  # 确保后续代码不执行文件读取

    else:
        # 如果什么都没指定，直接返回
        return y

    # 如果需要从文件加载噪音
    if noise_path:
        try:
            noise, sr_n = sf.read(noise_path)
        except FileNotFoundError:
            print(f"⚠️ 警告 (add_noise): 找不到噪音文件 {noise_path}，跳过此效果。")
            return y

        # 重采样和声道处理
        if sr_n != sr:
            noise = librosa.resample(noise.T, orig_sr=sr_n, target_sr=sr).T
        if noise.ndim > 1:
            noise = np.mean(noise, axis=1)
        if len(noise) < len(y):
            reps = int(np.ceil(len(y) / len(noise)))
            noise = np.tile(noise, reps)
        noise = noise[:len(y)]

    # --- 核心计算逻辑 (保持不变) ---
    rms_signal = np.sqrt(np.mean(y ** 2)) + 1e-8
    rms_noise_target = rms_signal * (10 ** (noise_db / 20.0))
    rms_noise_current = np.sqrt(np.mean(noise ** 2)) + 1e-8
    noise_scaled = noise * (rms_noise_target / rms_noise_current)

    # 混合并裁剪
    y_noisy = y + noise_scaled * wet
    return np.clip(y_noisy, -1.0, 1.0)