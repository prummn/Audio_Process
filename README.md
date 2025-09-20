# Batch Acoustic Scene Simulation Toolkit

这是一个为提升 ASR (自动语音识别) 模型鲁棒性而设计的批量化声学场景模拟工具包。它能够将干净的录音素材，通过灵活的配置，高效地处理成符合特定声学环境（如远场、嘈杂餐厅、会议室等）的增强数据。

## ✨ 核心特性

- **配置驱动**: 通过简单的 Python 配置文件定义复杂的音频效果链，无需改动核心代码。
- **批量处理**: 自动处理整个输入目录的音频，并按场景分类输出，专为大规模数据集生成而设计。
- **灵活执行**: 支持通过命令行参数选择性地运行一个或多个场景，便于测试和快速迭代。
- **智能噪音注入**: 支持从分类的噪音库中随机抽取背景音，极大丰富了生成数据的多样性。
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
pip install numpy librosa pydub pedalboard soundfile scipy pyloudnorm
```

### 2. 填充素材

1.  将你所有干净的原始 `.wav` 文件放入 `data_input/` 文件夹。
2.  在 `noises/` 文件夹下按类别创建子文件夹 (例如 `human_voice`, `mechanical`)，并放入相应的 `.wav` 噪音文件。

### 3. 定义一个场景

在 `configs/` 目录下创建一个新的配置文件，例如 `configs/car_interior_config.py`：

```python
# configs/car_interior_config.py

SCENE_CONFIG = {
    # 'scene_name' 将作为输出的子文件夹名
    "scene_name": "car_interior",

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

### 4. 执行处理

打开你的终端，使用 `batch_process.py` 脚本开始生成数据。

- **运行所有已定义的场景**:
  ```bash
  python batch_process.py
  ```

- **只运行指定的场景**:
  (文件名不带 `.py` 后缀)
  ```bash
  python batch_process.py car_interior
  ```

- **运行多个指定场景**:
  ```bash
  python batch_process.py car_interior far_field_config
  ```

所有处理完成的音频文件都将出现在 `data_output/` 目录下，并已按场景自动归类。