#!/usr/bin/env python3
"""Agnes 图片生成精简客户端"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://apihub.agnes-ai.com"
MODELS = {
    "2.1": "agnes-image-2.1-flash",
    "2.5": "agnes-image-2.5-flash",
}


def get_api_key() -> str:
    """仅从 AGNES_API_KEY 环境变量读取密钥"""
    value = os.environ.get("AGNES_API_KEY")
    if value:
        return value
    sys.exit("错误: 未设置 AGNES_API_KEY 环境变量")


def translate_prompt(prompt: str, api_key: str) -> str:
    """调用 agnes-2.0-flash 将非英文提示词翻译为英文"""
    body = {
        "model": "agnes-2.0-flash",
        "messages": [
            {"role": "system", "content": "Translate the following image generation prompt into fluent English. Preserve all visual details, style, lighting, composition and constraints. Output only the translated prompt."},
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        f"{API_BASE}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        print(f"警告: 翻译失败，直接使用原文 ({exc})", file=sys.stderr)
        return prompt


def call_image_api(prompt, model, size, input_image, api_key):
    """调用 Agnes 图片生成接口"""
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "extra_body": {"response_format": "url"},
    }
    if input_image:
        payload["extra_body"]["image"] = input_image

    req = urllib.request.Request(
        f"{API_BASE}/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code} 错误: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Agnes 图片生成精简客户端")
    parser.add_argument("-p", "--prompt", required=True, help="图片提示词")
    parser.add_argument("-m", "--model", default="2.1", choices=["2.1", "2.5"],
                        help="模型: 2.1=agnes-image-2.1-flash, 2.5=agnes-image-2.5-flash (默认 2.1)")
    parser.add_argument("-s", "--size", default="1024x1024", help="尺寸 (默认 1024x1024)")
    parser.add_argument("-i", "--image", action="append", default=[],
                        help="输入图片 URL (图生图/编辑, 可多次)")
    parser.add_argument("--no-translate", action="store_true", help="禁用自动翻译")
    args = parser.parse_args()

    api_key = get_api_key()
    model = MODELS[args.model]
    prompt = args.prompt

    if not args.no_translate and any(ord(c) > 127 for c in prompt):
        print("检测到非英文提示词, 正在翻译...", file=sys.stderr)
        prompt = translate_prompt(prompt, api_key)
        print(f"翻译后: {prompt}", file=sys.stderr)

    print(f"使用模型: {model} | 尺寸: {args.size}", file=sys.stderr)
    result = call_image_api(prompt, model, args.size, args.image or None, api_key)

    items = result.get("data") or []
    if items:
        for idx, item in enumerate(items, 1):
            url = item.get("url") or item.get("image_url") or json.dumps(item, ensure_ascii=False)
            print(url)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
