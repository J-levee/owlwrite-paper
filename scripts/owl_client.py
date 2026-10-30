#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OwlWrite 官方 HTTP 封装（2026-10-29）。

解决 Agent 直连服务端的三类高频坑：
  1) 忘带/错写 Content-Type → 服务端 422；本脚本对 POST/PUT 自动 application/json
  2) Bearer key 散落在对话/命令行里 → 统一从环境变量 OWL_API_KEY 或 ~/.owl_creds.json 读取
  3) 响应体散在终端里难复核 → --out 把原始 JSON 落盘，供技能包归档

用法：
  python owl_client.py request GET /v1/wallet
  python owl_client.py request POST /v1/quote --data '{"action":"write","params":{...}}' --out quote.json
  python owl_client.py claim-favorite D:/截图/收藏.png

凭据解析顺序：--key 参数 > 环境变量 OWL_API_KEY > ~/.owl_creds.json 的 owl_api_key 字段。
key 属敏感信息：不要写进对话、不要写进 SKILL 输出，只在本脚本进程内使用。
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = os.environ.get("OWL_BASE", "https://owl.skillsutra.cn")


def load_key(explicit=None):
    if explicit:
        return explicit.strip()
    k = os.environ.get("OWL_API_KEY", "").strip()
    if k:
        return k
    for p in (os.path.expanduser("~/.owl_creds.json"),
              os.path.expanduser("~/.workbuddy/owl_creds.json")):
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
                k = (d.get("owl_api_key") or d.get("api_key") or "").strip()
                if k:
                    return k
            except Exception:
                pass
    sys.exit("未找到 OWL_API_KEY：请设环境变量或写入 ~/.owl_creds.json（owl_api_key 字段）")


def call(method, path, data=None, key=None, base=None, timeout=120):
    url = (base or DEFAULT_BASE).rstrip("/") + path
    headers = {"Accept": "application/json"}
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"       # 坑 1：忘了就是 422
    # 坑 2：key 统一从环境/文件读——无条件解析，不能只在显式 --key 时带 Authorization
    #（否则环境变量/凭据文件路径静默失效，全部 401）
    headers["Authorization"] = "Bearer " + load_key(key)
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8") or "{}")
        except Exception:
            return e.code, {"raw": str(e)}


def claim_favorite(image_path, key=None, base=None):
    """提交 SkillHub 收藏截图审核。返回发放结果或拒单原因。"""
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        raw = f.read()
    if len(raw) > 5 * 1024 * 1024:
        sys.exit("截图超过 5MB，请压缩后重试")
    return call("POST", "/v1/campaign/favorite-claim",
                {"image_base64": base64.b64encode(raw).decode()},
                key=key, base=base, timeout=180)


def main():
    ap = argparse.ArgumentParser(description="OwlWrite 官方 HTTP 封装")
    ap.add_argument("cmd", choices=["request", "claim-favorite"])
    ap.add_argument("path_or_image", help="request: /v1/... 路径；claim-favorite: 截图路径")
    ap.add_argument("-X", "--method", default="GET", help="request 子命令用（GET/POST/...）")
    ap.add_argument("--data", help="JSON 请求体（字符串）")
    ap.add_argument("--out", help="响应 JSON 落盘路径（坑 3：方便归档复核）")
    ap.add_argument("--key", help="显式 API key（默认走环境/凭据文件）")
    ap.add_argument("--base", default=DEFAULT_BASE)
    a = ap.parse_args()

    if a.cmd == "claim-favorite":
        st, out = claim_favorite(a.path_or_image, key=a.key, base=a.base)
    else:
        data = json.loads(a.data) if a.data else None
        st, out = call(a.method.upper(), a.path_or_image, data, key=a.key, base=a.base)

    text = json.dumps(out, ensure_ascii=False, indent=2)
    print("HTTP", st)
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("已保存 ->", a.out)
    sys.exit(0 if st < 400 else 1)


if __name__ == "__main__":
    main()
