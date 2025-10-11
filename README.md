# Batch Acoustic Scene Simulation Toolkit

这是一个为提升 ASR (自动语音识别) 模型鲁棒性而设计的批量化声学场景模拟工具包。它能够将干净的录音素材，通过灵活的配置，高效地处理成符合特定声学环境（如远场、嘈杂餐厅、会议室等）的增强数据。

## ✨ 核心特性

- **配置驱动**: 通过简单的 Python 配置文件定义复杂的音频效果链，无需改动核心代码。
- **参数随机化**: 支持在配置文件中为参数指定一个范围或选项列表，在处理每个文件时随机采样，极大丰富数据多样性。
- **批量处理**: 自动处理整个输入目录的音频，并按场景分类输出，专为大规模数据集生成而设计。
- **灵活执行**: 支持通过命令行参数选择性地运行一个或多个场景，便于测试和快速迭代。
- **智能噪音注入**: 支持从分类的噪音库中随机抽取背景音。
- **专业响度控制**: 采用行业标准的 LUFS 进行响度归一化，精确模拟音量衰减等听感效果。
- **模块化与可扩展**: 所有效果均为独立模块，方便用户修改或添加自定义的音频处理功能。

## 📂 项目结构

```
/
├── configs/                  # 场景配置库
├── data_input/               # 原始音频素材库
├── data_output/              # 处理结果输出库
├── effects/                  # 音频效果模块包
├── noises/                   # 分类噪音素材库
└── batch_process.py          # 批量处理主脚本
```

## 🚀 快速开始

### 1. 环境准备

首先，请安装所有必需的 Python 库：
```bash
pip install numpy librosa soundfile pedalboard pyloudnorm
```
*(注意: pydub 和 scipy 可能是一些效果模块的间接依赖)*

### 2. 填充素材

1.  将你所有干净的原始 `.wav` 文件放入 `data_input/` 文件夹。
2.  在 `noises/` 文件夹下按类别创建子文件夹 (例如 `human_voice`, `mechanical`, `street`)，并放入相应的 `.wav` 噪音文件。

### 3. 定义一个场景

在 `configs/` 目录下创建一个新的配置文件。配置的核心是定义一个名为 `SCENE_CONFIG` 的字典。

#### 示例 1: 固定参数配置

这是一个基础示例，所有参数都是固定值。

```python
# configs/car_interior_config.py

SCENE_CONFIG = {
    # 'scene_name' 将作为输出的子文件夹名
    "scene_name": "car_interior_static",

    "effects": [
        # 效果1: 应用一个低通滤波器，模拟车内沉闷的环境
        {
            "name": "apply_filter",
            "params": {
                "filter_type": "lowpass",
                "cutoff_hz": 4000
            }
        },
        # 效果2: 从 'mechanical' 类别中随机选择一个噪音 (如引擎声)
        {
            "name": "add_noise",
            "params": {
                "noise_category": "mechanical",
                "noise_db": -15  # 噪音较大
            }
        }
    ]
}
```

#### 示例 2: 高级配置 - 使用随机参数

为了生成更多样化的数据，您可以为参数指定一个范围或选项列表，脚本在处理**每个文件**时都会从中随机采样一个值。

```python
# configs/cocktail_party_config.py

SCENE_CONFIG = {
    "scene_name": "cocktail_party_randomized",

    "effects": [
        {
            "name": "add_reverb",
            "params": {
                # 在 0.3 到 0.7 之间随机选择一个浮点数作为房间大小
                "room_size": {"random_type": "uniform", "min": 0.3, "max": 0.7},
                "damping": 0.8,
                "wet_level": {"random_type": "uniform", "min": 0.2, "max": 0.5},
            }
        },
        {
            "name": "add_noise",
            "params": {
                # 从 'human_voice' 目录随机选一个噪音文件
                "noise_category": "human_voice",
                # 在 3 到 15 之间随机选择一个整数作为信噪比
                "noise_db": {"random_type": "randint", "min": 3, "max": 15}
            }
        },
        {
            "name": "adjust_speed",
            "params": {
                # adjust_speed 效果本身就在 min 和 max 之间随机，用法保持不变
                "speed_min": 0.9,
                "speed_max": 1.1
            }
        }
    ]
}
```
**支持的随机类型 (`random_type`)**:
- `"uniform"`: 在 `min` 和 `max` 之间随机采样一个 **浮点数**。
- `"randint"`: 在 `min` 和 `max` 之间随机采样一个 **整数**。
- `"choice"`: 从 `options` 列表中随机选择 **一项** (例如: `{"random_type": "choice", "options": ["A", "B", "C"]}` )。

### 4. 执行处理

打开您的终端，使用 `batch_process.py` 脚本开始生成数据。

- **运行所有已定义的场景**:
  ```bash
  python batch_process.py
  ```

- **只运行一个指定的场景**:
  提供配置文件的**基本名称** (不带 `.py` 后缀) 作为参数。
  ```bash
  python batch_process.py cocktail_party_config
  ```

- **运行多个指定场景**:
  将所有想运行的配置文件基本名作为参数，用空格隔开。
  ```bash
  python batch_process.py cocktail_party_config car_interior_config
  ```

所有处理完成的音频文件都将出现在 `data_output/` 目录下，并已按场景名称 (`scene_name`) 自动归类。