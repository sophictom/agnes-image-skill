---
name: agnes-image
description: "Call Agnes AI image models (agnes-image-2.1-flash / agnes-image-2.5-flash) for text-to-image and image-to-image generation. Use when the user asks to use Agnes API, Agnes Image, or to generate/edit images via Agnes."
---

# Agnes 图片生成技能

通过 `https://apihub.agnes-ai.com` 调用 Agnes 图片模型，仅支持图片生成/编辑，不支持视频。

## 前置条件
- 环境变量 `AGNES_API_KEY` 已设置
- Python 3.10+，无需第三方依赖（仅用标准库）

## 使用方式
始终通过 `scripts/agnes_image.py` 调用，不要手写 curl 或重复造轮子。

### 文生图（默认 2.1 模型）
```bash
python scripts/agnes_image.py -p "A luminous floating city above a misty canyon at sunrise"
```

### 文生图（2.5 模型）
```bash
python scripts/agnes_image.py -m 2.5 -p "A cute orange cat sitting on windowsill in rain"
```

### 中文提示词（自动翻译为英文再生成）
```bash
python scripts/agnes_image.py -m 2.5 -p "一只橘猫坐在雨天的窗台上，电影感写实风格"
```

### 指定尺寸
```bash
python scripts/agnes_image.py -m 2.5 -p "cyberpunk night market" -s 1024x768
```

### 图生图 / 编辑
```bash
python scripts/agnes_image.py -m 2.5 -p "Turn into rainy night" -i https://example.com/input.png
```

### 禁用自动翻译
```bash
python scripts/agnes_image.py --no-translate -p "already english prompt"
```

## 工作流规则
- 文生图优先用 `agnes-image-2.1-flash`，图生图/编辑或高细节需求优先用 `agnes-image-2.5-flash`
- 非英文提示词默认先调用 `agnes-2.0-flash` 翻译为英文再发送，提升生成稳定性
- 生成结果直接返回 URL，不要主动下载媒体文件，除非用户明确要求
- 如果请求失败，报告 HTTP 状态码和错误内容，不要暴露 API Key
- 不要使用这个 skill 生成视频；视频请用其他方式
