"""DKF 命令行入口。

用法：
  dkf scan      # K01 元数据扫描 -> .dkf/meta/
  dkf index     # K07 构建索引   -> .dkf/index/
  dkf domains   # 生成 K02 领域划分草稿（待 AI/人工填充）-> .dkf/domains/

配置：默认读当前目录 config.yaml，或用 --config 指定。
凭据建议放环境变量，不要写进 config 提交到 Git。
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import yaml

from .auth import DataverseAuth
from .client import DataverseClient
from .k01_scan import run_k01, scan_solutions, scan_code_logic, build_code_flow_md
from .k04_skeleton import build_skeletons
from .k07_index import build_index


def _load_config(path: str) -> dict:
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    dv = cfg["dataverse"]
    # 环境变量覆盖（凭据优先走 env）
    dv["client_secret"] = os.environ.get("DKF_CLIENT_SECRET", dv.get("client_secret", ""))
    dv["client_id"] = os.environ.get("DKF_CLIENT_ID", dv.get("client_id", ""))
    return cfg


def _client(cfg: dict) -> DataverseClient:
    dv = cfg["dataverse"]
    auth = DataverseAuth(dv["tenant_id"], dv["client_id"], dv["client_secret"], dv["resource_url"])
    return DataverseClient(auth, page_size=cfg.get("page_size", 500))


def cmd_check(cfg: dict, out: Path):
    """连通性自检：调 WhoAmI，确认认证 + 应用用户配置通了。"""
    client = _client(cfg)
    print(f"[check] 连接 {cfg['dataverse']['resource_url']} ...")
    who = client.get_one("WhoAmI")
    print("  ✓ 认证成功")
    print(f"  UserId         = {who.get('UserId')}")
    print(f"  BusinessUnitId = {who.get('BusinessUnitId')}")
    print(f"  OrganizationId = {who.get('OrganizationId')}")
    print("[check] 通过：可以跑 scan 了。")


def cmd_scan(cfg: dict, out: Path):
    client = _client(cfg)
    custom_only = cfg.get("custom_only", True)
    print(f"[K01] 开始扫描 {cfg['dataverse']['resource_url']} (custom_only={custom_only}) ...")
    summary = run_k01(client, out, custom_only=custom_only)
    for name, n in summary.items():
        print(f"  ✓ {name}: {n} 条")
    print(f"[K01] 完成 -> {out/'meta'}")


def cmd_index(cfg: dict, out: Path):
    print("[K07] 构建系统地图索引 ...")
    p = build_index(out)
    print(f"[K07] 完成 -> {p}")


def cmd_domains(cfg: dict, out: Path):
    """生成 K02 草稿：把实体按 标准模块前缀/自定义前缀 做初步分桶，等 AI+人工细化。"""
    meta = out / "meta"
    topo = json.loads((meta / "K01_C_entity_topology.json").read_text(encoding="utf-8"))
    buckets: dict[str, list] = {}
    for e in topo["entities"]:
        ln = e["logicalname"]
        # 简单启发式：用 publisher 前缀(prefix_) 或标准实体名做初分；真正的领域划分交给 K02 prompt
        prefix = ln.split("_")[0] + "_" if "_" in ln else "(standard)"
        buckets.setdefault(prefix, []).append(ln)
    dom = out / "domains"
    dom.mkdir(parents=True, exist_ok=True)
    draft = {"_note": "这是按前缀的机器初分，请用 prompts/K02_domain_division.md 让 AI 按业务语义重划，再人工 K03 确认",
             "buckets": buckets}
    (dom / "K02_draft.json").write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[K02] 草稿已生成 -> {dom/'K02_draft.json'}（{len(buckets)} 个前缀桶）")


def cmd_code(cfg: dict, out: Path, code_dir: Path):
    """K09 代码逻辑补充：扫 code/ 源码，把插件碰的实体/环境变量补进 .dkf/meta/。"""
    print(f"[K09] 扫描代码逻辑 {code_dir} ...")
    res = scan_code_logic(code_dir)
    meta = out / "meta"; meta.mkdir(parents=True, exist_ok=True)
    (meta / "K09_code_logic.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if res.get("note"):
        print(f"  ⚠️ {res['note']}")
    print(f"  ✓ {len(res['files'])} 个源码文件有逻辑信号 -> {meta/'K09_code_logic.json'}")
    # 流程图（Mermaid）
    idx = out / "index"; idx.mkdir(parents=True, exist_ok=True)
    (idx / "K09_code_flow.md").write_text(build_code_flow_md(res), encoding="utf-8")
    print(f"  ✓ 代码流程图 -> {idx/'K09_code_flow.md'}")


def cmd_k04(cfg: dict, out: Path, with_attributes: bool = False):
    client = _client(cfg) if with_attributes else None
    print("[K04] 生成领域知识骨架 ...")
    written = build_skeletons(out, client=client, with_attributes=with_attributes)
    for p in written:
        print(f"  ✓ {p}")
    print(f"[K04] 完成 {len(written)} 个领域 -> {out/'skills'}")


def main():
    ap = argparse.ArgumentParser(prog="dkf", description="Dynamics Knowledge Flow 扫描器")
    ap.add_argument("command", choices=["check", "scan", "index", "domains", "k04", "code"])
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--out", default=".dkf")
    ap.add_argument("--with-attributes", action="store_true",
                    help="k04 时实时拉每个实体的自定义字段（需可连 Dataverse）")
    ap.add_argument("--code-dir", default="code",
                    help="code 命令扫描的源码目录（默认 ./code）")
    args = ap.parse_args()

    cfg = _load_config(args.config)
    out = Path(args.out)
    if args.command == "k04":
        cmd_k04(cfg, out, with_attributes=args.with_attributes)
    elif args.command == "code":
        cmd_code(cfg, out, Path(args.code_dir))
    else:
        {"check": cmd_check, "scan": cmd_scan, "index": cmd_index, "domains": cmd_domains}[args.command](cfg, out)


if __name__ == "__main__":
    main()
