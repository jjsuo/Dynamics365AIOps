"""K04 半自动：为每个确认领域生成知识 Skill 骨架。

把"找数据"这件确定性的事自动做掉——从 K01 元数据里把本域相关的
实体、流程、业务入口、安全自动填进骨架；只把"业务逻辑/坑点"留给 AI+人工。

输入：
  .dkf/domains/K03_confirmed.json   （K03 人工确认的领域）
  .dkf/meta/*.json                  （K01 扫描产物）
可选：传入 client + --with-attributes，则实时拉每个实体的自定义字段。

输出：.dkf/skills/<domain>.md（骨架，🤖 自动段已填，✍️ 段待 AI 补）
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .k01_scan import scan_entity_attributes


def _load(meta: Path, name: str, default=None):
    p = meta / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def _slug(name: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff-]+", "_", name).strip("_")


def build_skeletons(out_dir: Path, client=None, with_attributes: bool = False) -> list[Path]:
    meta = out_dir / "meta"
    domains_file = out_dir / "domains" / "K03_confirmed.json"
    if not domains_file.exists():
        raise FileNotFoundError("缺少 .dkf/domains/K03_confirmed.json（请先做完 K02/K03）")

    domains = json.loads(domains_file.read_text(encoding="utf-8")).get("domains", [])
    entry = _load(meta, "K01_A_entry_points.json", {}) or {}
    procs = _load(meta, "K01_P_processes.json", []) or []
    security = _load(meta, "K01_G_security.json", {}) or {}

    plugin_steps = entry.get("plugin_steps", [])
    custom_apis = entry.get("custom_apis", [])

    skills_dir = out_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for dom in domains:
        ents = set(dom.get("entities", []))
        name = dom["name"]

        # 自动匹配：entity 落在本域的流程/插件/入口
        dom_procs = [p for p in procs if p.get("entity") in ents]
        dom_steps = [s for s in plugin_steps if s.get("entity") in ents]
        dom_apis = [a for a in custom_apis if a.get("bound_entity") in ents]

        lines = [
            f"# 领域知识：{name}  (type: {dom.get('type','-')})",
            "",
            "> 半自动骨架：🤖 段已由扫描器自动填充（指向真实元数据）；✍️ 段需 AI + 人工补。",
            "> 生成后用 `prompts/K04_domain_knowledge.md` 让 AI 补全 1/6 段。",
            "",
            "## 1. 域概述  ✍️",
            "<待补：这个域解决什么业务问题，边界在哪，与相邻域怎么切>",
            "",
            "## 2. 核心实体  🤖",
            "| 实体 | 类型 | 自定义字段 |",
            "|---|---|---|",
        ]
        for ln in sorted(ents):
            attrs = "（见 .dkf/meta，或加 --with-attributes 拉取）"
            if with_attributes and client is not None:
                try:
                    a = scan_entity_attributes(client, ln)
                    attrs = ", ".join(x["logicalname"] for x in a) or "（无自定义字段）"
                except Exception as ex:  # 单实体失败不影响整体
                    attrs = f"（拉取失败：{ex}）"
            kind = "自定义" if ln.split("_")[0] not in ("account", "contact") and "_" in ln else "标准/共享"
            lines.append(f"| {ln} | {kind} | {attrs} |")

        lines += ["", "## 3. 关键业务流程  🤖"]
        if dom_procs:
            for p in dom_procs:
                lines.append(f"- {p['category']}：**{p['name']}**（entity: {p['entity']}，{p['state']}）")
        else:
            lines.append("- （本域实体上未扫到流程）")

        lines += ["", "## 4. 业务入口 / 集成点  🤖"]
        if dom_steps or dom_apis:
            for s in dom_steps:
                lines.append(f"- 插件 `{s['name']}`：{s['message']}@{s['stage']} {s['mode']}（{s['entity']}）")
            for a in dom_apis:
                lines.append(f"- Custom API `{a['uniquename']}`（bound: {a['bound_entity']}）")
        else:
            lines.append("- （本域实体上未扫到插件/Custom API）")

        lines += ["", "## 5. 安全模型  🤖→✍️",
                  f"- 全局共 {len(security.get('roles', []))} 个安全角色、"
                  f"{len(security.get('teams', []))} 个团队，详见 `.dkf/meta/K01_G_security.json`",
                  "- ✍️ 待补：本域读写涉及哪些角色，有无字段级安全",
                  "",
                  "## 6. 坑点与约定  ✍️",
                  "<待补：实施时容易踩的、客户特有的业务规则、历史包袱>",
                  ""]

        out = skills_dir / f"{_slug(name)}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        written.append(out)

    return written
