#!/usr/bin/env bash
# 离线验证：零云端、一条命令看 DKF 框架的完整产出。
# 用 samples/ 里的 mock 元数据，跑 domains / k04 / index 三步，打印结果。
# 目的：在做任何 Entra/Dataverse/飞书 设置之前，先判断"产出对我有没有用"。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DKF_PKG="$ROOT/dkf"
WORK="$ROOT/samples/output"           # 产出目录（可随时删）
OUT="$WORK/.dkf"

echo "================ DKF 离线验证 ================"
echo "（使用 samples/ 的 mock 元数据，不连任何云端服务）"
echo

# 0) 依赖检查
python3 -c "import yaml, requests" 2>/dev/null || {
  echo "缺少依赖，先装：pip install -r dkf/requirements.txt"; exit 1; }

# 1) 准备工作目录：把 mock 元数据放到 .dkf/ 结构里
rm -rf "$WORK"; mkdir -p "$OUT/meta" "$OUT/domains"
cp "$ROOT/samples/meta/"*.json       "$OUT/meta/"
cp "$ROOT/samples/K03_confirmed.json" "$OUT/domains/"
# k04 需要一个最简 config（仅 --with-attributes 才真用，这里离线不需要）
cp "$DKF_PKG/config.example.yaml" "$WORK/config.yaml"

export PYTHONPATH="$DKF_PKG:${PYTHONPATH:-}"
cd "$WORK"

# 2) 跑流程（全部离线可跑）
echo "---- [1/3] domains：按前缀初分领域 ----"
python3 -m dkf.cli domains --out "$OUT"
echo
echo "---- [2/3] k04：自动生成领域知识骨架 ----"
python3 -m dkf.cli k04 --out "$OUT"
echo
echo "---- [3/3] index：构建系统地图 ----"
python3 -m dkf.cli index --out "$OUT"

# 3) 打印关键产出供肉眼判断
echo
echo "================ 产出 1：系统地图 (K07) ================"
cat "$OUT/index/system_map.md"
echo
echo "================ 产出 2：领域知识骨架 (K04) — 合同管理 ================"
cat "$OUT/skills/合同管理.md"
echo
echo "================ 产出 3：领域知识骨架 (K04) — 备件派工 ================"
cat "$OUT/skills/备件派工.md"

echo
echo "============================================================"
echo "✅ 验证完成。所有产出在：$OUT"
echo "   - meta/      mock 输入（真实环境由 scan 自动生成）"
echo "   - skills/    K04 领域知识骨架（🤖 自动填 / ✍️ 待 AI 补）"
echo "   - index/     system_map.md 系统地图 + entity_hooks.json"
echo
echo "判断标准：把 skills/ 和 index/ 喂给你的 AI agent，问它一个业务问题"
echo "（如\"合同到期逻辑在哪\"），看它能否据此指到正确的实体/流程/插件。"
echo "觉得有用 → 再去做云端设置跑真实 scan；不满意 → 改 k01_scan.py 和模板。"
