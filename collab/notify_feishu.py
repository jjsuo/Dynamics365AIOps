"""协作层：把 DAF 的阶段门禁推到飞书话题，等异步放行。

实现"话题=并行最小治理单元"：每个模块一个话题(thread)，阶段到达
pending_review 时往话题里发一张门禁卡片，顾问/架构师在手机或桌面上
回复 `yes` 放行 / `e + 意见` 退回。

用法：
  # 给某个群发一张门禁卡片（开一个新话题）
  python notify_feishu.py --chat <chat_id> --module 合同管理 --stage P03 \
      --summary "Fit-Gap=配置；FDD 已出；待功能顾问放行" --artifacts FDD/REQ-001.md

  # 在已有话题里回复（保持在同一话题线程内）
  python notify_feishu.py --reply <root_message_id> --module 合同管理 --stage P05 ...

前置：飞书应用开通 im:message:send / im:message（发消息）；机器人已入群。
app_secret 走环境变量 FEISHU_APP_SECRET。
国际版 Lark 把 BASE 改为 https://open.larksuite.com。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import requests

BASE = "https://open.feishu.cn"

STAGE_GATES = {  # 哪些阶段是强制人工门禁
    "P03": "Fit-Gap & FDD（功能顾问/架构师拍板）",
    "P05": "概要设计 SDD（架构师放行）",
    "S06": "Solution Checker + 代码/配置评审",
    "S07": "打包部署到 UAT",
    "T01": "UAT 业务流程验收",
}


def tenant_token(app_id: str, app_secret: str) -> str:
    r = requests.post(f"{BASE}/open-apis/auth/v3/tenant_access_token/internal",
                      json={"app_id": app_id, "app_secret": app_secret}, timeout=30)
    r.raise_for_status()
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"取 token 失败: {d}")
    return d["tenant_access_token"]


STATUS_STYLE = {  # 进度通知样式
    "in_progress": ("blue", "⏳ 进行中"),
    "done":        ("green", "✅ 完成"),
    "blocked":     ("red", "⛔ 阻塞"),
}


def build_progress_card(module: str, step: str, status: str, detail: str) -> dict:
    """进度卡片：长操作(建实体/字段、扫描、部署)的开始/完成/阻塞即时通知。
    与门禁卡片区分——进度卡片不需要回复放行，只是告知。"""
    color, label = STATUS_STYLE.get(status, ("grey", status))
    return {
        "config": {"wide_screen_mode": True},
        "header": {"template": color,
                   "title": {"tag": "plain_text", "content": f"{label} · {module} · {step}"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": detail or "(无详情)"}},
            {"tag": "note", "elements": [{"tag": "lark_md",
             "content": "进度通知 · 无需回复"}]},
        ],
    }


def build_gate_card(module: str, stage: str, summary: str, artifacts: list[str]) -> dict:
    gate_desc = STAGE_GATES.get(stage, stage)
    arts = "\n".join(f"• {a}" for a in artifacts) or "（无）"
    return {
        "config": {"wide_screen_mode": True},
        "header": {"template": "orange",
                   "title": {"tag": "plain_text", "content": f"🚦 门禁 · {module} · {stage}"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**门禁**：{gate_desc}"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**摘要**：{summary}"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**产物**：\n{arts}"}},
            {"tag": "hr"},
            {"tag": "note", "elements": [{"tag": "lark_md",
             "content": "在本话题回复 `yes` 放行 ｜ `e + 意见` 退回修改"}]},
        ],
    }


def send_to_chat(token: str, chat_id: str, card: dict) -> str:
    url = f"{BASE}/open-apis/im/v1/messages?receive_id_type=chat_id"
    body = {"receive_id": chat_id, "msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False)}
    r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body, timeout=30)
    r.raise_for_status()
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"发送失败: {d}")
    return d["data"]["message_id"]


def reply_in_thread(token: str, root_message_id: str, card: dict) -> str:
    """回复到某条消息所在话题，reply_in_thread=True 保持在同一话题线程。"""
    url = f"{BASE}/open-apis/im/v1/messages/{root_message_id}/reply"
    body = {"msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False),
            "reply_in_thread": True}
    r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body, timeout=30)
    r.raise_for_status()
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"回复失败: {d}")
    return d["data"]["message_id"]


def main():
    ap = argparse.ArgumentParser(description="DAF 通知 -> 飞书话题（门禁卡片 / 进度卡片）")
    ap.add_argument("--module", required=True)
    # 门禁模式：--stage + --summary；进度模式：--status + --step + --detail
    ap.add_argument("--stage", help="门禁阶段(P03/P05/S06/S07/T01)，门禁卡片用")
    ap.add_argument("--summary", help="门禁摘要")
    ap.add_argument("--artifacts", nargs="*", default=[])
    ap.add_argument("--status", choices=["in_progress", "done", "blocked"],
                    help="进度通知：长操作开始/完成/阻塞（无需回复）")
    ap.add_argument("--step", help="进度通知的步骤名，如 'S03 建实体字段'")
    ap.add_argument("--detail", default="", help="进度详情")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--chat", help="chat_id：在群里开新话题")
    g.add_argument("--reply", help="root_message_id：在已有话题里回复")
    ap.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""))
    args = ap.parse_args()

    secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not args.app_id or not secret:
        sys.exit("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET")

    token = tenant_token(args.app_id, secret)
    if args.status:  # 进度卡片
        card = build_progress_card(args.module, args.step or "", args.status, args.detail)
        kind = "进度卡片"
    else:            # 门禁卡片
        if not args.stage or not args.summary:
            sys.exit("门禁卡片需 --stage 和 --summary（或用 --status 走进度卡片）")
        card = build_gate_card(args.module, args.stage, args.summary, args.artifacts)
        kind = "门禁卡片"
    mid = send_to_chat(token, args.chat, card) if args.chat else reply_in_thread(token, args.reply, card)
    print(f"已发送{kind}，message_id={mid}")


if __name__ == "__main__":
    main()
