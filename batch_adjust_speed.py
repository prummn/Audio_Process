import os
import librosa
import soundfile as sf
import numpy as np

# --- 配置 ---
# 要扫描的根目录
TARGET_DIR = "data_output_grid"
# 要应用的固定速度倍率列表
SPEEDS_TO_APPLY = [0.5, 1.25, 2.0]


def adjust_speed(y, sr, rate):
    """
    以指定的速率改变音频的播放速度。

    参数:
    y (np.ndarray): 输入的音频数据 NumPy 数组。
    sr (int): 音频的采样率 (Hz)。
    rate (float): 目标速度倍率。

    返回:
    np.ndarray: 改变速度后的音频数据。
    """
    try:
        # 使用 librosa 进行时间拉伸，不改变音高
        y_stretched = librosa.effects.time_stretch(y, rate=rate)
        return y_stretched.astype(np.float32)
    except Exception as e:
        print(f"    ❌ 调整速度时出错: {e}")
        return None


def main():
    """
    主函数，遍历目标目录并为所有 .wav 文件创建多倍速版本。
    """
    print(f"--- 开始为 '{TARGET_DIR}' 目录下的音频批量调整速度 ---")
    print(f"将为每个文件创建以下倍速版本: {SPEEDS_TO_APPLY}")

    # 递归遍历目标目录
    audio_files_to_process = []
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            # 检查文件是否为 .wav 且不是已经处理过的文件
            if file.lower().endswith('.wav') and '_speed_' not in file.lower():
                audio_files_to_process.append(os.path.join(root, file))

    if not audio_files_to_process:
        print("\n未找到需要处理的音频文件。任务结束。")
        return

    print(f"\n共找到 {len(audio_files_to_process)} 个音频文件待处理。")

    total_files_created = 0
    # 遍历所有找到的音频文件
    for filepath in audio_files_to_process:
        print(f"\n处理文件: {filepath}")

        try:
            # 加载原始音频
            y_original, sr = librosa.load(filepath, sr=None, mono=True)
        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}。已跳过。")
            continue

        # 获取文件名和目录，用于构建新文件名
        directory, filename = os.path.split(filepath)
        base_name, ext = os.path.splitext(filename)

        # 为每个指定的倍速创建一个版本
        for speed in SPEEDS_TO_APPLY:
            print(f"  - 正在生成 {speed:.2f}x 倍速版本...")

            # 调整速度
            y_new = adjust_speed(y_original, sr, rate=speed)

            if y_new is not None:
                # 构建新的输出文件名，例如: "original_name_speed_0.50x.wav"
                new_filename = f"{base_name}_speed_{speed:.2f}x{ext}"
                output_path = os.path.join(directory, new_filename)

                # 保存新的音频文件
                try:
                    sf.write(output_path, y_new, sr)
                    print(f"    ✅ 已保存至: {output_path}")
                    total_files_created += 1
                except Exception as e:
                    print(f"    ❌ 保存文件失败: {e}")

    print(f"\n--- 所有任务完成 ---")
    print(f"总共创建了 {total_files_created} 个新的倍速音频文件。")


if __name__ == "__main__":
    main()