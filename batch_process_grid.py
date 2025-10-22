import os
import sys
import importlib
import librosa
import soundfile as sf
import copy
import random
import itertools

# --- 固定目录路径 (与原脚本一致) ---
INPUT_DIR = "data_input_grid"
OUTPUT_DIR = "data_output_grid"
CONFIGS_DIR = "configs"
NOISES_DIR = "noises"
EFFECTS_PACKAGE = "effects"


# --- 辅助函数 (与原脚本一致) ---
def _resolve_random_params(params_dict):
    """解析非核心的随机参数。"""
    for key, value in params_dict.items():
        if isinstance(value, dict) and "random_type" in value:
            rand_type = value.get("random_type")
            try:
                if rand_type == "uniform":
                    params_dict[key] = random.uniform(value["min"], value["max"])
                elif rand_type == "randint":
                    params_dict[key] = random.randint(value["min"], value["max"])
                elif rand_type == "choice":
                    params_dict[key] = random.choice(value["options"])
            except KeyError as e:
                print(f"  ⚠️ 随机参数 '{key}' 缺少键: {e}，将保持原样。")


def load_configs(config_dir, specific_configs=None):
    """动态加载配置文件 (与原脚本一致)。"""
    # ... (此处代码与原 batch_process.py 完全相同，为简洁省略)
    # 您可以直接从原文件复制 load_configs 函数的全部代码到这里
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
                    config_files_to_load.append(available_file);
                    found = True;
                    break
            if not found: print(f"⚠️ 警告：找不到指定的配置文件 '{fname}'，已跳过。")
    else:
        config_files_to_load = available_files
    if not config_files_to_load: return []
    sys.path.insert(0, os.path.abspath(config_dir))
    for filename in config_files_to_load:
        module_name = filename[:-3]
        try:
            if module_name in sys.modules: importlib.reload(sys.modules[module_name])
            module = importlib.import_module(module_name)
            if hasattr(module, 'SCENE_CONFIG'):
                configs.append(module.SCENE_CONFIG)
                print(f"✅ 成功加载场景配置: {module.SCENE_CONFIG.get('scene_name', '未知')}")
        except Exception as e:
            print(f"⚠️ 加载配置文件 {filename} 失败: {e}")
    sys.path.pop(0)
    return configs


def process_audio_file(filepath, output_path, effect_chain, combination_params):
    """
    对单个音频文件应用效果链。
    新增 `combination_params` 参数来注入核心参数的特定组合值。
    """
    try:
        y, sr = librosa.load(filepath, sr=None)
    except Exception as e:
        print(f"  ❌ 读取文件 {filepath} 失败: {e}")
        return

    processed_y = y
    for effect_config in effect_chain:
        effect_name = effect_config.get("name")
        params = copy.deepcopy(effect_config.get("params", {}))

        # 1. 注入当前组合的核心参数值
        if effect_name in combination_params:
            for param_name, param_value in combination_params[effect_name].items():
                params[param_name] = param_value

        # 2. 随机化处理非核心的参数
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
    """主函数，执行基于网格搜索的批量处理流程。"""
    print("--- 开始批量制造场景模拟数据 (网格搜索模式) ---")

    specific_configs_to_run = sys.argv[1:] if len(sys.argv) > 1 else None

    if specific_configs_to_run:
        print(f"指定模式：将只运行以下场景 -> {', '.join(specific_configs_to_run)}")
    else:
        print("自动模式：将运行 'configs' 目录下的所有场景。")

    scene_configs = load_configs(CONFIGS_DIR, specific_configs_to_run)
    if not scene_configs: return

    input_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.wav')]
    if not input_files:
        print(f"错误：在 '{INPUT_DIR}' 目录中未找到任何 .wav 文件。")
        return

    print(f"\n找到 {len(scene_configs)} 个待处理场景和 {len(input_files)} 个输入文件。")

    for config in scene_configs:
        scene_name = config["scene_name"]
        effect_chain = config["effects"]

        # --- 核心逻辑：识别核心参数并生成组合 ---
        core_params_map = {}
        for effect in effect_chain:
            effect_name = effect["name"]
            for param_name, param_config in effect.get("params", {}).items():
                if isinstance(param_config, dict) and param_config.get("is_core"):
                    if effect_name not in core_params_map:
                        core_params_map[effect_name] = {}

                    min_val, max_val = param_config["min"], param_config["max"]
                    core_params_map[effect_name][param_name] = {
                        'low': min_val,
                        'mid': (min_val + max_val) / 2,
                        'high': max_val
                    }

        if not core_params_map:
            print(f"\n--- 场景 '{scene_name}' 未指定核心参数，已跳过 (此脚本仅处理带核心参数的场景) ---")
            continue

        # 构建所有可能的组合
        param_names_with_levels = []
        for effect_name, params in core_params_map.items():
            for param_name, levels in params.items():
                param_names_with_levels.append(
                    [(effect_name, param_name, level_name, level_value) for level_name, level_value in levels.items()])

        all_combinations = list(itertools.product(*param_names_with_levels))
        num_combinations = len(all_combinations)

        print(
            f"\n--- 正在处理场景: {scene_name} (发现 {len(core_params_map)} 个核心参数, 将生成 {num_combinations} 种组合) ---")

        for input_path in input_files:
            original_filename = os.path.basename(input_path)
            original_base_name, _ = os.path.splitext(original_filename)
            print(f"处理文件: {original_filename}")

            variant_output_dir = os.path.join(OUTPUT_DIR, scene_name, original_base_name)

            for i, combo in enumerate(all_combinations):
                combination_params = {}
                name_parts = []

                for effect_name, param_name, level_name, level_value in combo:
                    if effect_name not in combination_params:
                        combination_params[effect_name] = {}
                    combination_params[effect_name][param_name] = level_value
                    # 简化命名，例如 "reverb-room_size-low" -> "room_size-low"
                    name_parts.append(f"{param_name}-{level_name}")

                combo_name_suffix = "_".join(name_parts)
                new_filename = f"{original_base_name}_{combo_name_suffix}.wav"
                output_path = os.path.join(variant_output_dir, new_filename)

                print(f"  - 生成组合 {i + 1}/{num_combinations} ({combo_name_suffix})...")

                process_audio_file(input_path, output_path, effect_chain, combination_params)
                print(f"    ✅ 已保存至: {output_path}")

    print("\n--- 所有任务完成 ---")


if __name__ == "__main__":
    main()