import os
import sys
import importlib
import librosa
import soundfile as sf
import copy
import random

# --- 固定目录路径 ---
INPUT_DIR = "data_input"
OUTPUT_DIR = "data_output"
CONFIGS_DIR = "configs"
NOISES_DIR = "noises"
EFFECTS_PACKAGE = "effects"


def _resolve_random_params(params_dict):
    """
    解析参数字典，将定义为范围的参数随机化为具体值。
    这个函数会直接修改传入的字典。
    """
    for key, value in params_dict.items():
        if isinstance(value, dict) and "random_type" in value:
            rand_type = value.get("random_type")
            try:
                if rand_type == "uniform":
                    min_val = value["min"]
                    max_val = value["max"]
                    params_dict[key] = random.uniform(min_val, max_val)
                elif rand_type == "randint":
                    min_val = value["min"]
                    max_val = value["max"]
                    params_dict[key] = random.randint(min_val, max_val)
                elif rand_type == "choice":
                    options = value["options"]
                    params_dict[key] = random.choice(options)
                else:
                    print(f"  ⚠️ 未知的随机类型 '{rand_type}'，参数 '{key}' 将保持原样。")
            except KeyError as e:
                print(f"  ⚠️ 随机参数 '{key}' 缺少必要的键: {e}，将保持原样。")
            except Exception as e:
                print(f"  ⚠️ 处理随机参数 '{key}' 时出错: {e}，将保持原样。")


def load_configs(config_dir, specific_configs=None):
    """
    动态加载配置文件。
    如果提供了 specific_configs 列表，则只加载这些配置。
    否则，加载 config_dir 中的所有配置。
    """
    configs = []
    config_files_to_load = []

    available_files = [f for f in os.listdir(config_dir) if f.endswith('.py') and not f.startswith('__')]

    if specific_configs:
        for spec_name in specific_configs:
            fname = f"{spec_name}.py" if not spec_name.endswith('.py') else spec_name
            fname_base = fname[:-3]

            found = False
            for available_file in available_files:
                if available_file == fname or available_file.startswith(fname_base):
                    config_files_to_load.append(available_file)
                    found = True
                    break
            if not found:
                print(f"⚠️ 警告：找不到指定的配置文件 '{fname}'，已跳过。")
    else:
        config_files_to_load = available_files

    if not config_files_to_load:
        return []

    sys.path.insert(0, os.path.abspath(config_dir))
    for filename in config_files_to_load:
        module_name = filename[:-3]
        try:
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

        _resolve_random_params(params)

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


def main():
    """主函数，执行批量处理流程。"""
    print("--- 开始批量制造场景模拟数据 ---")

    args = sys.argv[1:]
    specific_configs_to_run = []
    num_variants_cmd = None

    for arg in args:
        if arg.startswith('--num-variants='):
            try:
                num_variants_cmd = int(arg.split('=')[1])
                if num_variants_cmd < 1:
                    print("⚠️ 警告：--num-variants 必须是大于0的整数。将忽略此参数。")
                    num_variants_cmd = None
            except (ValueError, IndexError):
                print(f"⚠️ 警告：无效的 --num-variants 参数格式。示例: --num-variants=5。")
        else:
            specific_configs_to_run.append(arg)

    if not specific_configs_to_run:
        specific_configs_to_run = None

    if specific_configs_to_run:
        print(f"指定模式：将只运行以下场景 -> {', '.join(specific_configs_to_run)}")
    else:
        print("自动模式：将运行 'configs' 目录下的所有场景。")

    if num_variants_cmd is not None:
        print(f"命令行指定：将为每个输入音频生成 {num_variants_cmd} 个副本。")

    scene_configs = load_configs(CONFIGS_DIR, specific_configs_to_run)
    if not scene_configs:
        print("错误：未找到任何有效的场景配置文件来运行。")
        return

    input_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.wav')]
    if not input_files:
        print(f"错误：在 '{INPUT_DIR}' 目录中未找到任何 .wav 文件。")
        return

    print(f"\n找到 {len(scene_configs)} 个待处理场景和 {len(input_files)} 个输入文件。")

    for config in scene_configs:
        scene_name = config["scene_name"]
        effect_chain = config["effects"]

        if num_variants_cmd is not None:
            num_variants = num_variants_cmd
        else:
            num_variants = config.get("num_variants", 1)

        print(f"\n--- 正在处理场景: {scene_name} (每个输入将生成 {num_variants} 个副本) ---")

        for input_path in input_files:
            original_filename = os.path.basename(input_path)
            original_base_name, _ = os.path.splitext(original_filename)
            print(f"处理文件: {original_filename}")

            # --- 核心改动：构建以原始文件名命名的子文件夹路径 ---
            variant_output_dir = os.path.join(OUTPUT_DIR, scene_name, original_base_name)
            # ----------------------------------------------------

            for i in range(1, num_variants + 1):
                if num_variants > 1:
                    new_filename = f"{original_base_name}_variant_{i}.wav"
                    print(f"  - 生成副本 {i}/{num_variants}...")
                else:
                    new_filename = original_filename

                # --- 核心改动：使用新的子文件夹路径来构建最终输出路径 ---
                output_path = os.path.join(variant_output_dir, new_filename)
                # ----------------------------------------------------

                process_audio_file(input_path, output_path, effect_chain)
                print(f"    ✅ 已保存至: {output_path}")

    print("\n--- 所有任务完成 ---")


if __name__ == "__main__":
    main()