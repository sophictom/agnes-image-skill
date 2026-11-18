# Agnes Image Skill

[中文](#中文) | [English](#english)

---

## 中文

一个用于调用 **Agnes AI 图片模型** 的 Agent Skill，支持文生图与图生图/图片编辑，通过 [apihub.agnes-ai.com](https://apihub.agnes-ai.com) 接口调用。

### ✨ 特性

- 🖼️ **文生图**：输入提示词即可生成图片，支持自定义尺寸
- 🎨 **图生图 / 编辑**：传入一张或多张参考图进行重绘或编辑
- 🇨🇳 **中文提示词直传**：无需先翻译成英文，实测直传效果好
- 🔁 **自动重试**：429 / 5xx / 网络错误自动重试最多 3 次（指数退避）
- 📦 **零依赖**：仅使用 Python 标准库（3.10+），无需安装任何第三方包
- 💾 **可选下载**：`--download` 可将生成结果保存到本地目录
- 🔇 **管道友好**：stdout 只输出图片 URL，诊断信息走 stderr

### 🧩 支持的模型

| 模型 | 说明 |
| --- | --- |
| `agnes-image-2.5-flash` | **默认**，图生图 / 编辑 / 高细节需求首选 |
| `agnes-image-2.1-flash` | 备选，适合快速文生图 |

### 🚀 快速开始

```bash
# 1. 设置 API Key（环境变量）
export AGNES_API_KEY="your-api-key"

# 2. 文生图（默认 2.5 模型）
python scripts/agnes_image.py -p "A luminous floating city above a misty canyon at sunrise"

# 3. 中文提示词直传
python scripts/agnes_image.py -p "一只橘猫坐在雨天的窗台上，电影感写实风格"

# 4. 图生图 / 编辑（支持多图）
python scripts/agnes_image.py -p "Turn into rainy night" -i https://example.com/input.png

# 5. 指定尺寸 / 切换模型 / 下载到本地
python scripts/agnes_image.py -m 2.1 -p "cyberpunk night market" -s 1024x768 --download --out-dir ./outputs
```

### 📖 参数说明

| 参数 | 说明 |
| --- | --- |
| `-p/--prompt` | 必填，图片提示词，支持中文直传 |
| `-m/--model` | `2.1` / `2.5`（默认），对应 `agnes-image-*.flash` |
| `-s/--size` | 图片尺寸，默认 `1024x1024` |
| `-i/--image` | 输入图片 URL，可重复传入多张，用于图生图/编辑 |
| `--download` | 生成后下载到本地 |
| `--out-dir` | 下载目录，默认 `./outputs` |

### 📁 目录结构

```
agnes-image-skill/
├── SKILL.md              # Skill 定义与使用说明（给 Agent 看的）
├── README.md             # 本文件
└── scripts/
    └── agnes_image.py    # 精简客户端脚本（仅标准库）
```

---

## English

An Agent Skill for calling **Agnes AI image models**, supporting text-to-image and image-to-image / editing via the [apihub.agnes-ai.com](https://apihub.agnes-ai.com) API.

### ✨ Features

- 🖼️ **Text-to-Image**: Generate images from prompts with custom sizes
- 🎨 **Image-to-Image / Editing**: Pass one or more reference images for redraw or edit
- 🇨🇳 **Chinese prompts as-is**: No translation step needed — direct pass works great in practice
- 🔁 **Auto retry**: Up to 3 retries with exponential backoff on 429 / 5xx / network errors
- 📦 **Zero dependency**: Python standard library only (3.10+), nothing to install
- 💾 **Optional download**: `--download` saves generated images to a local directory
- 🔇 **Pipeline friendly**: stdout prints only image URLs; diagnostics go to stderr

### 🧩 Supported Models

| Model | Notes |
| --- | --- |
| `agnes-image-2.5-flash` | **Default**; preferred for img2img / editing / high detail |
| `agnes-image-2.1-flash` | Alternative for fast text-to-image |

### 🚀 Quick Start

```bash
# 1. Set your API key (environment variable)
export AGNES_API_KEY="your-api-key"

# 2. Text-to-image (default 2.5 model)
python scripts/agnes_image.py -p "A luminous floating city above a misty canyon at sunrise"

# 3. Chinese prompt, passed as-is
python scripts/agnes_image.py -p "一只橘猫坐在雨天的窗台上，电影感写实风格"

# 4. Image-to-image / editing (multi-image supported)
python scripts/agnes_image.py -p "Turn into rainy night" -i https://example.com/input.png

# 5. Custom size / model switch / download locally
python scripts/agnes_image.py -m 2.1 -p "cyberpunk night market" -s 1024x768 --download --out-dir ./outputs
```

### 📖 CLI Options

| Option | Description |
| --- | --- |
| `-p/--prompt` | Required. Image prompt (Chinese supported, passed as-is) |
| `-m/--model` | `2.1` / `2.5` (default), maps to `agnes-image-*.flash` |
| `-s/--size` | Image size, default `1024x1024` |
| `-i/--image` | Input image URL for img2img/editing; repeatable for multiple images |
| `--download` | Download generated images after completion |
| `--out-dir` | Download directory, default `./outputs` |

### 📁 Project Structure

```
agnes-image-skill/
├── SKILL.md              # Skill definition & usage guide (for agents)
├── README.md             # This file
└── scripts/
    └── agnes_image.py    # Minimal client script (stdlib only)
```

---

## License / 许可

个人使用 / For personal use.
