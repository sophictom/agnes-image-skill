#!/usr/bin/env python3
"""Agnes 图片生成精简客户端（v2）

设计要点：
- 仅依赖 Python 标准库
- 中文提示词直接送入图片模型（实测直传效果良好），不做英文翻译
- 主接口失败自动重试（429/5xx/网络错误，最多 3 次，指数退避）
- 支持多张输入图（-i 可重复），图生图/编辑时以列表传入 extra_body.image
- stdout/stderr 强制 UTF-8，规避 Windows 控制台乱码
- 支持将生成图片下载到本地目录（默认 ./outputs）
- 任何输出绝不包含 API Key
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ---- Windows 控制台 UTF-8 修正 ----
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

API_BASE = "https://apihub.agnes-ai.com"
# 可用图片模型（以 /v1/models 实测为准）
MODELS = {
    "2.1": "agnes-image-2.1-flash",
    "2.5": "agnes-image-2.5-flash",
}
DEFAULT_MODEL = "2.5"
DEFAULT_OUT_DIR = Path("./outputs").resolve()
MAX_RETRIES = 3
RETRY_STATUS = {429, 500, 502, 503, 504}


def get_api_key() -> str:
    value = os.environ.get("AGNES_API_KEY", "").strip()
    if not value:
        sys.exit("错误: 未设置 AGNES_API_KEY 环境变量")
    return value


def _request_json(req: urllib.request.Request, timeout: int) -> dict:
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _post_json_with_retry(path: str, body: dict, api_key: str, timeout: int) -> dict:
    """POST JSON，对 429/5xx/网络错误自动重试（指数退避），4xx 直接报错。"""
    last_err = ""
    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(
            f"{API_BASE}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            return _request_json(req, timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            last_err = f"HTTP {exc.code}: {detail}"
            if exc.code in RETRY_STATUS and attempt < MAX_RETRIES:
                wait = 2 ** attempt
                print(f"警告: 第 {attempt} 次请求失败（{last_err.splitlines()[0][:120]}），{wait}s 后重试...",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"错误: 接口请求失败，{last_err}")
        except urllib.error.URLError as exc:
            last_err = f"网络错误: {exc.reason}"
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                print(f"警告: 第 {attempt} 次请求失败（{last_err}），{wait}s 后重试...", file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"错误: 网络不可达（已重试 {MAX_RETRIES} 次）: {exc.reason}")
    sys.exit(f"错误: 请求失败，{last_err}")


def call_image_api(prompt: str, model: str, size: str,
                   input_images: list[str], api_key: str) -> dict:
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "extra_body": {"response_format": "url"},
    }
    if input_images:
        # 单图传字符串，多图传列表，避免覆盖
        payload["extra_body"]["image"] = input_images[0] if len(input_images) == 1 else input_images

    print(f"调用模型: {model} | 尺寸: {size} | 输入图: {len(input_images)} 张", file=sys.stderr)
    return _post_json_with_retry("/v1/images/generations", payload, api_key, 180)


def download(url: str, out_dir: Path, prefix: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{prefix}-{time.strftime('%Y%m%d-%H%M%S')}.png"
    req = urllib.request.Request(url, headers={"User-Agent": "agnes-image-skill/2.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(target, "wb") as fh:
        fh.write(resp.read())
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Agnes 图片生成精简客户端（中文直传，无翻译）")
    parser.add_argument("-p", "--prompt", required=True, help="图片提示词（支持中文，直接使用）")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, choices=list(MODELS),
                        help=f"图片模型: {' / '.join(f'{k}={v}' for k, v in MODELS.items())}（默认 {DEFAULT_MODEL}）")
    parser.add_argument("-s", "--size", default="1024x1024", help="尺寸，例如 1024x1024 / 1024x768")
    parser.add_argument("-i", "--image", action="append", default=None, metavar="URL",
                        help="图生图/编辑的输入图片 URL，可重复传入多张")
    parser.add_argument("--download", action="store_true", help="生成完成后下载到本地")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="下载目录，默认 ./outputs")
    args = parser.parse_args()

    api_key = get_api_key()
    result = call_image_api(args.prompt, MODELS[args.model], args.size,
                            args.image or [], api_key)

    items = result.get("data") or []
    if not items:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    out_dir = Path(args.out_dir).resolve()
    for idx, item in enumerate(items, 1):
        url = item.get("url") or item.get("image_url")
        if not url:
            print(f"[item {idx}] {json.dumps(item, ensure_ascii=False)}")
            continue
        print(url)
        if args.download:
            try:
                path = download(url, out_dir, f"agnes-{args.model}-{idx}")
                print(f"已下载: {path}", file=sys.stderr)
            except Exception as exc:
                print(f"警告: 下载失败 ({exc})", file=sys.stderr)


if __name__ == "__main__":
    main()
