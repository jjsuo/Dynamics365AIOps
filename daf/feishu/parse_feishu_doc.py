"""飞书需求文档 → 纯文本（喂给 P01 需求采集）。

用法：
  python parse_feishu_doc.py --doc <document_id>            # docx 文档
  python parse_feishu_doc.py --doc <document_id> --out req.txt

前置：
  1. 飞书开放平台建一个企业自建应用，拿到 app_id / app_secret
  2. 开通权限：docx:document:readonly（读取文档）
  3. 把应用加入目标文档的协作者（或开放给应用可见）
  4. app_secret 走环境变量 FEISHU_APP_SECRET

说明：document_id 是飞书文档 URL 里 /docx/ 后面那串。
本脚本用 raw_content 端点直接取纯文本，足够 P01 拆需求；
若要保留结构（标题层级/表格），改用 /blocks 端点遍历 block。
"""
from __future__ import annotations

import argparse
import os
import sys
import requests

BASE = "https://open.feishu.cn"  # 国际版改为 https://open.larksuite.com


def tenant_token(app_id: str, app_secret: str) -> str:
    url = f"{BASE}/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"取 token 失败: {data}")
    return data["tenant_access_token"]


def get_raw_content(token: str, document_id: str) -> str:
    url = f"{BASE}/open-apis/docx/v1/documents/{document_id}/raw_content"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"取文档失败: {data}")
    return data["data"]["content"]


def main():
    ap = argparse.ArgumentParser(description="飞书需求文档抓取 (P01 输入)")
    ap.add_argument("--doc", required=True, help="飞书 docx document_id")
    ap.add_argument("--out", default="-", help="输出文件，默认 stdout")
    ap.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""))
    args = ap.parse_args()

    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not args.app_id or not app_secret:
        sys.exit("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET 环境变量")

    token = tenant_token(args.app_id, app_secret)
    content = get_raw_content(token, args.doc)

    if args.out == "-":
        print(content)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"已写入 {args.out}（{len(content)} 字）", file=sys.stderr)


if __name__ == "__main__":
    main()
