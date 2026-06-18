#!/usr/bin/env bash
# D365 AI 交付范式 — 一键安装到你的项目仓。
#
# 别人在【他自己的项目仓根目录】跑：
#   curl -fsSL <RAW_URL>/install.sh | bash
# 或克隆本仓后跑：  bash /path/to/install.sh
#
# 它做三件事，且只碰【框架】、绝不动你的项目数据：
#   1. 把框架作为 git submodule 钉在 .daf-framework/（锁定版本，可复现）
#   2. 跑 `daf sync` 生成各 agent 适配器（AGENTS.md / .claude/commands / .kiro/steering / copilot）
#   3. 写 daf.lock 记录版本
#
# 之后更新： bash .daf-framework/install.sh --update   （或 python3 .daf-framework/bin/daf update）
set -euo pipefail

REPO_URL="${DAF_REPO_URL:-https://github.com/YOUR_ORG/d365-ai-paradigm.git}"
VENDOR_DIR=".daf-framework"
REF="${DAF_REF:-main}"          # 可传 tag/commit 钉死版本：DAF_REF=v0.2.0

err() { echo "❌ $*" >&2; exit 1; }
command -v git >/dev/null   || err "需要 git"
command -v python3 >/dev/null || err "需要 python3"

# 必须在一个 git 仓里（submodule 需要）
git rev-parse --show-toplevel >/dev/null 2>&1 || err "请在你的项目 git 仓根目录运行（先 git init）"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if [[ "${1:-}" == "--update" ]]; then
  echo "[update] 更新框架副本 ..."
  if [[ -f .gitmodules ]] && grep -q "$VENDOR_DIR" .gitmodules 2>/dev/null; then
    git submodule update --remote --merge "$VENDOR_DIR"
  else
    git -C "$VENDOR_DIR" pull --ff-only
  fi
else
  if [[ -d "$VENDOR_DIR" ]]; then
    echo "[install] $VENDOR_DIR 已存在，改为更新"
    git -C "$VENDOR_DIR" pull --ff-only || true
  else
    echo "[install] 添加框架 submodule -> $VENDOR_DIR （$REPO_URL @ $REF）"
    git submodule add -b "$REF" "$REPO_URL" "$VENDOR_DIR" 2>/dev/null \
      || git clone --branch "$REF" "$REPO_URL" "$VENDOR_DIR"
  fi
fi

# PyYAML 是驱动唯一依赖
python3 -c "import yaml" 2>/dev/null || pip install --quiet PyYAML || pip3 install --quiet PyYAML

echo "[sync] 生成 agent 适配器 ..."
python3 "$VENDOR_DIR/bin/daf" sync

VER="$(python3 "$VENDOR_DIR/bin/daf" version)"
{ echo "framework: $VER"; echo "ref: $REF"; echo "vendored: $VENDOR_DIR"; \
  echo "updated: $(date -u +%FT%TZ)"; } > daf.lock

cat <<EOF

✅ 安装完成：$VER
   - 适配器已生成：AGENTS.md / .claude/commands/daf.md / .kiro/steering/daf.md / .github/copilot-instructions.md
   - 你的 agent 现在执行：daf list  →  daf show <步骤>  →  按步交付
   - DKF 需配 Dataverse：cp $VENDOR_DIR/dkf/config.example.yaml dkf/config.yaml

下次更新框架： bash $VENDOR_DIR/install.sh --update
EOF
