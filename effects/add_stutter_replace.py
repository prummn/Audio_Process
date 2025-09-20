import numpy as np


def process(y, sr, frame_ms=20, stutter_prob=0.05, repeat_prob=0.75, max_repeats=3):
    """
    通过随机“替换”音频帧来模拟卡顿效果，保持音频总长度不变。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    frame_ms (int): 每个音频帧的长度（毫秒）。这是处理的基本单位。
    stutter_prob (float): 任何一帧触发卡顿事件的概率 (0 到 1)。
    repeat_prob (float): 触发卡顿后，是“重复”上一帧（卡顿）还是“丢弃”当前帧（静音）的概率。
    max_repeats (int): 一次卡顿事件中，最多连续替换多少帧。

    返回:
    np.ndarray: 处理后的音频数据，长度与输入相同。
    """
    frame_length = int(sr * frame_ms / 1000)
    if frame_length == 0:
        raise ValueError("frame_ms is too small, resulting in a frame_length of 0.")

    # 创建一个输入的副本，我们将直接在它上面进行修改
    y_processed = np.copy(y)

    pos = 0
    last_frame = np.zeros(frame_length, dtype=y.dtype)

    while pos < len(y):
        # 确定当前帧的边界
        end = min(pos + frame_length, len(y))
        current_frame = y[pos:end]

        # 随机决定是否触发卡顿
        if np.random.rand() < stutter_prob:
            repeat_count = np.random.randint(1, max_repeats + 1)

            for i in range(repeat_count):
                # 计算将要被替换的帧的位置
                replace_pos = pos + (i * frame_length)
                replace_end = min(replace_pos + frame_length, len(y))

                if replace_pos >= len(y):
                    break  # 如果替换位置超出音频末尾，则停止

                # 随机决定是重复上一帧还是用静音替换
                if np.random.rand() < repeat_prob:
                    # 用上一帧的内容替换掉当前位置的帧
                    write_len = min(frame_length, replace_end - replace_pos)
                    y_processed[replace_pos:replace_end] = last_frame[:write_len]
                else:
                    # 用静音替换掉当前位置的帧
                    y_processed[replace_pos:replace_end] = 0

            # 重要：指针需要跳过所有被替换的帧
            pos += repeat_count * frame_length
        else:
            # 正常情况，更新 last_frame 并移动指针
            if len(current_frame) < frame_length:
                last_frame = np.pad(current_frame, (0, frame_length - len(current_frame)), 'constant')
            else:
                last_frame = current_frame

            pos += frame_length

    return y_processed