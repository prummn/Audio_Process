import os
import sys
import importlib
import librosa
import soundfile as sf
import copy

# --- 固定目录路径 ---
INPUT_DIR = "data_input"
OUTPUT_DIR = "data_output"
CONFIGS_DIR = "configs"
NOISES_DIR = "noises"
EFFECTS_PACKAGE = "effects"


def load_configs(config_dir, specific_configs=None):
    """
    动态加载配置文件。
    如果提供了 specific_configs 列表，则只加载这些配置。
    否则，加载 config_dir 中的所有配置。
    """
    configs = []
    config_files_to_load = []

    # 获取所有可用的配置文件名
    available_files = [f for f in os.listdir(config_dir) if f.endswith('.py') and not f.startswith('__')]

    if specific_configs:
        # 如果用户指定了配置文件，则只加载这些
        for spec_name in specific_configs:
            fname = f"{spec_name}.py"
            if fname in available_files:
                config_files_to_load.append(fname)
            else:
                print(f"⚠️ 警告：找不到指定的配置文件 '{fname}'，已跳过。")
    else:
        # 如果未指定，则加载所有
        config_files_to_load = available_files

    if not config_files_to_load:
        return []

    # 动态导入选定的模块
    sys.path.insert(0, os.path.abspath(config_dir))
    for filename in config_files_to_load:
        module_name = filename[:-3]
        try:
            # 如果模块已被加载，先重新加载以确保获取最新更改
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])

            module = importlib.import_module(module_name)
            if hasattr(module, 'SCENE_CONFIG'):
                configs.append(module.SCENE_CONFIG)
                print(f"✅ 成功加载场景配置: {module.SCENE_CONFIG.get('scene_name', '未知')}")
        except Exception as e:
            print(f"⚠️ 加载配置文件 {filename} 失败: {e}")
    sys.path.pop(0)
    return configs


def process_audio_file(filepath, output_path, effect_chain):
    """对单个音频文件应用效果链。"""
    try:
        y, sr = librosa.load(filepath, sr=None)
    except Exception as e:
        print(f"  ❌ 读取文件 {filepath} 失败: {e}")
        return

    processed_y = y
    for effect_config in effect_chain:
        effect_name = effect_config.get("name")
        params = copy.deepcopy(effect_config.get("params", {}))

        try:
            module_path = f"{EFFECTS_PACKAGE}.{effect_name}"
            effect_module = importlib.import_module(module_path)
            process_func = getattr(effect_module, "process")

            if effect_name == "add_noise":
                params['noise_dir'] = NOISES_DIR

            processed_y = process_func(processed_y, sr, **params)

        except Exception as e:
            print(f"  ❌ 应用效果 '{effect_name}' 时出错: {e}")
            return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, processed_y, sr)
    print(f"  ✅ 已保存至: {output_path}")


def main():
    """主函数，执行批量处理流程。"""
    print("--- 开始批量制造场景模拟数据 ---")

    # 1. 从命令行参数获取要运行的特定配置
    # sys.argv[0] 是脚本名, sys.argv[1:] 是所有后续参数
    specific_configs_to_run = sys.argv[1:] if len(sys.argv) > 1 else None

    if specific_configs_to_run:
        print(f"指定模式：将只运行以下场景 -> {', '.join(specific_configs_to_run)}")
    else:
        print("自动模式：将运行 'configs' 目录下的所有场景。")

    # 2. 加载场景配置
    scene_configs = load_configs(CONFIGS_DIR, specific_configs_to_run)
    if not scene_configs:
        print("错误：未找到任何有效的场景配置文件来运行。")
        return

    # 3. 获取所有输入音频文件
    input_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.wav')]
    if not input_files:
        print(f"错误：在 '{INPUT_DIR}' 目录中未找到任何 .wav 文件。")
        return

    print(f"\n找到 {len(scene_configs)} 个待处理场景和 {len(input_files)} 个输入文件。")

    # 4. 遍历每个场景，处理所有音频文件
    for config in scene_configs:
        scene_name = config["scene_name"]
        effect_chain = config["effects"]
        scene_output_dir = os.path.join(OUTPUT_DIR, scene_name)

        print(f"\n--- 正在处理场景: {scene_name} ---")

        for input_path in input_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(scene_output_dir, filename)
            print(f"处理文件: {filename}")
            process_audio_file(input_path, output_path, effect_chain)

    print("\n--- 所有任务完成 ---")


if __name__ == "__main__":
    main()