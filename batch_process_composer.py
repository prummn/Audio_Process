import os
import sys
import importlib
import copy
import itertools
import librosa
import soundfile as sf
import random

# --- 固定目录路径 ---
INPUT_DIR = "data_input"
OUTPUT_DIR = "data_output_composer"
CONFIGS_DIR = "configs"
NOISES_DIR = "noises"
EFFECTS_PACKAGE = "effects"


def load_all_configs(config_dir):
    """
    加载并返回 configs 目录下所有有效的场景配置。
    """
    configs = []
    sys.path.insert(0, os.path.abspath(config_dir))
    for filename in os.listdir(config_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                module = importlib.import_module(module_name)
                if hasattr(module, 'SCENE_CONFIG'):
                    configs.append(module.SCENE_CONFIG)
            except Exception as e:
                print(f"⚠️ 加载配置文件 {filename} 失败: {e}")
    sys.path.pop(0)
    return configs


def combine_effect_chains(overlay_effects, base_effects):
    """
    智能合并效果链。
    规则：以叠加特性的效果链为基础，只从基底场景中添加前者没有的、独有的效果器。
    """
    # 深拷贝叠加效果链，作为合并的基础
    combined_effects = copy.deepcopy(overlay_effects)

    # 获取叠加特性中已有的所有效果器名称
    overlay_effect_names = {effect['name'] for effect in overlay_effects}

    # 遍历基底场景的效果链
    for base_effect in base_effects:
        # 如果这个效果器不在叠加特性中，就把它添加进最终的效果链
        if base_effect['name'] not in overlay_effect_names:
            combined_effects.append(base_effect)

    return combined_effects


def _resolve_random_params(params_dict):
    """
    解析参数字典，将定义为范围的参数随机化为具体值。
    """
    for key, value in list(params_dict.items()):
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


def process_audio_file(filepath, output_path, effect_chain):
    """
    对单个音频文件应用一个完整的、已合并的效果链。
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
    """
    主函数，智能组合场景，并支持通过命令行参数进行筛选和控制。
    """
    print("--- 开始批量制造场景模拟数据 (智能组合模式) ---")

    # --- 解析命令行参数 ---
    num_variants = 1
    target_bases = None
    target_overlays = None
    args = sys.argv[1:]

    for arg in args:
        if arg.startswith('--num-variants='):
            try:
                num_variants = int(arg.split('=')[1])
                if num_variants < 1: num_variants = 1
            except (ValueError, IndexError):
                print(f"⚠️ 警告：无效的 --num-variants 参数格式。将使用默认值 1。")
        elif arg.startswith('--base='):
            try:
                target_bases = arg.split('=')[1].split(',')
            except IndexError:
                print("⚠️ 警告：--base 参数格式无效，已忽略。")
        elif arg.startswith('--overlay='):
            try:
                target_overlays = arg.split('=')[1].split(',')
            except IndexError:
                print("⚠️ 警告：--overlay 参数格式无效，已忽略。")

    if num_variants > 1:
        print(f"命令行指定：将为每个输入音频在每个组合场景下生成 {num_variants} 个副本。")
    if target_bases: print(f"目标基底场景已指定: {target_bases}")
    if target_overlays: print(f"目标叠加特性已指定: {target_overlays}")

    # 1. 加载并筛选配置
    all_configs = load_all_configs(CONFIGS_DIR)
    base_scenes_all = [c for c in all_configs if c.get("metadata", {}).get("scene_type") == "base"]
    overlay_features_all = [c for c in all_configs if c.get("metadata", {}).get("scene_type") == "overlay"]

    base_scenes = [s for s in base_scenes_all if target_bases is None or s['scene_name'] in target_bases]
    overlay_features = [f for f in overlay_features_all if
                        target_overlays is None or f['scene_name'] in target_overlays]

    if not base_scenes or not overlay_features:
        print("\n错误：经过筛选后，有效的 'base' 和 'overlay' 场景不足以进行组合。")
        return

    print(f"\n将使用 {len(base_scenes)} 个基底场景: {[s['scene_name'] for s in base_scenes]}")
    print(f"将使用 {len(overlay_features)} 个叠加特性: {[f['scene_name'] for f in overlay_features]}")

    # 2. 生成组合
    all_combinations = list(itertools.product(overlay_features, base_scenes))
    print(f"将生成 {len(all_combinations)} 种场景组合。")

    input_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.wav')]
    if not input_files:
        print(f"错误：在 '{INPUT_DIR}' 目录中未找到任何 .wav 文件。")
        return

    # 3. 遍历并处理
    for overlay_config, base_config in all_combinations:
        combined_scene_name = f"{base_config['scene_name']}_with_{overlay_config['scene_name']}"

        # --- 核心改动：使用新的智能合并函数 ---
        combined_effect_chain = combine_effect_chains(overlay_config['effects'], base_config['effects'])
        # ------------------------------------

        print(f"\n--- 正在处理组合场景: {combined_scene_name} ---")
        print(f"  合并后的效果链: {[e['name'] for e in combined_effect_chain]}")

        for input_path in input_files:
            original_filename = os.path.basename(input_path)
            base_name, ext = os.path.splitext(original_filename)
            print(f"    处理文件: {original_filename}")

            output_dir_for_audio = os.path.join(OUTPUT_DIR, combined_scene_name, base_name)

            for i in range(1, num_variants + 1):
                if num_variants > 1:
                    new_filename = f"{base_name}_variant_{i}{ext}"
                    print(f"      - 生成副本 {i}/{num_variants}...")
                else:
                    new_filename = original_filename

                output_path = os.path.join(output_dir_for_audio, new_filename)

                process_audio_file(input_path, output_path, combined_effect_chain)
                print(f"        ✅ 已保存至: {output_path}")

    print("\n--- 所有组合场景处理完成 ---")


if __name__ == "__main__":
    main()