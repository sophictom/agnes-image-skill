---
name: agnes-image
description: "Call Agnes AI image models (agnes-image-2.1-flash / agnes-image-2.5-flash) for text-to-image and image-to-image generation, with optional download to local disk. Use when the user asks to use Agnes API, Agnes Image, or to generate/edit images via Agnes."
---

# Agnes 图片生成技能

通过 `https://apihub.agnes-ai.com` 调用 Agnes 图片模型，仅支持图片生成/编辑，不支持视频。

## 前置条件
- 环境变量 `AGNES_API_KEY` 已设置（本机存于系统级环境变量）
- Python 3.10+，仅使用标准库，无需安装依赖

## 模型现状（2026-11 以 /v1/models 实测为准）
- 图片模型：`agnes-image-2.1-flash`、`agnes-image-2.5-flash`（**默认 2.5**）
- 对话模型仅剩 `agnes-2.5-flash` / `agnes-3.0-flash`，`agnes-2.0-flash` 已下线
- **本 skill 不做提示词翻译**：中文提示词直接传入图片模型，实测直传效果好，翻译链路徒增失败点

## 使用方式

始终通过 `scripts/agnes_image.py` 调用，不要手写 curl 或重复造轮子。

### 文生图（默认 2.5 模型）
```bash
python scripts/agnes_image.py -p "A luminous floating city above a misty canyon at sunrise"
```

### 中文提示词直传
```bash
python scripts/agnes_image.py -p "一只橘猫坐在雨天的窗台上，电影感写实风格"
```

### 指定尺寸 / 切换模型
```bash
python scripts/agnes_image.py -m 2.1 -p "cyberpunk night market" -s 1024x768
```

### 图生图 / 编辑（支持多图）
```bash
python scripts/agnes_image.py -p "Turn into rainy night" -i https://example.com/input.png
python scripts/agnes_image.py -p "Merge these two styles" -i URL1 -i URL2   # 多图以列表传入
```

### 下载到本地并展示
```bash
python scripts/agnes_image.py -p "一只橘猫坐在窗台" --download --out-dir ./outputs
```
`--download` 会把图片存到本地目录（默认 `./outputs`）并打印绝对路径，便于在客户端直接预览。

## 参数说明
| 参数 | 说明 |
| --- | --- |
| `-p/--prompt` | 必填，图片提示词，支持中文直传 |
| `-m/--model` | `2.1` / `2.5`（默认），对应 `agnes-image-*.flash` |
| `-s/--size` | 默认 `1024x1024` |
| `-i/--image` | 输入图片 URL，可重复传多张，用于图生图/编辑 |
| `--download` | 生成后下载到本地 |
| `--out-dir` | 下载目录，默认当前工作目录下 `outputs` |

## 行为约定
- **无翻译步骤**：中文提示词原样直传，不要为提示词单独调用对话模型
- 内置失败重试：429/5xx/网络错误自动重试最多 3 次（指数退避），其余 4xx 立即报错
- 脚本输出：stdout 只有图片 URL（便于管道处理）；诊断信息与下载后的本地绝对路径走 stderr
- 桌面端用户要求预览/保存时，加 `--download` 并把 stderr 中的本地路径展示给用户
- 若最终失败，报告 HTTP 状态码与错误内容，**绝不输出 API Key**
- 不要用本 skill 生成视频，视频请使用其他方案
