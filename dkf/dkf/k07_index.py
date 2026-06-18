"""K07 AI 索引：把 K01 扫描产物汇总成一份可检索的"系统地图"。

输出 .dkf/index/system_map.md —— 给 AI 当导航用：
  - 每个实体出现在哪些流程/插件/集成入口里
  - 反向索引：message+entity -> 触发了哪些插件步骤
这一步只做"指针汇总"，不复述元数据细节（继承 VKF 索引而非翻译的原则）。
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def _load(meta: Path, name: str):
    p = meta / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def build_index(out_dir: Path) -> Path:
    meta = out_dir / "meta"
    idx_dir = out_dir / "index"
    idx_dir.mkdir(parents=True, exist_ok=True)

    topo = _load(meta, "K01_C_entity_topology.json") or {}
    entry = _load(meta, "K01_A_entry_points.json") or {}
    procs = _load(meta, "K01_P_processes.json") or []

    # 按实体聚合：每个实体涉及哪些插件步骤 / 流程
    by_entity = defaultdict(lambda: {"plugin_steps": [], "processes": []})
    for s in entry.get("plugin_steps", []):
        if s.get("entity"):
            by_entity[s["entity"]]["plugin_steps"].append(
                f"{s['message']}@{s['stage']}({s['mode']})")
    for p in procs:
        if p.get("entity"):
            by_entity[p["entity"]]["processes"].append(f"{p['category']}:{p['name']}")

    lines = ["# DKF 系统地图（K07 AI 索引）", "",
             "> 本文件是导航索引。看到具体实体/流程后，回到 `.dkf/meta/` 的原始元数据，",
             "> 或直接查 Dataverse 定义，不要以本文件的转述为准。", ""]

    ents = topo.get("entities", [])
    lines.append(f"## 实体清单（{len(ents)} 个）\n")
    for e in sorted(ents, key=lambda x: x["logicalname"]):
        ln = e["logicalname"]
        hooks = by_entity.get(ln, {})
        steps = hooks.get("plugin_steps", [])
        ps = hooks.get("processes", [])
        tag = "自定义" if e.get("is_custom") else "标准"
        line = f"- **{ln}** [{tag}]"
        if steps:
            line += f" · 插件: {', '.join(steps)}"
        if ps:
            line += f" · 流程: {', '.join(ps)}"
        lines.append(line)

    out = idx_dir / "system_map.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    # 同时产出机器可读索引
    machine = {ln: by_entity[ln] for ln in by_entity}
    (idx_dir / "entity_hooks.json").write_text(
        json.dumps(machine, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
