#!/usr/bin/env bash
# S07 — 用 Power Platform CLI (pac) 把 solution 导出 + 源码化进 Git。
# 前置：安装 pac CLI；pac auth create 已登录目标环境。
#   dotnet tool install --global Microsoft.PowerApps.CLI.Tool
#   pac auth create --environment https://yourorg.crm5.dynamics.com
set -euo pipefail

SOLUTION_NAME="${1:?用法: solution_export.sh <SolutionUniqueName> [src_dir]}"
SRC_DIR="${2:-./solutions/${SOLUTION_NAME}}"
TMP_ZIP="/tmp/${SOLUTION_NAME}_managed.zip"

echo "[S07] 导出 managed solution: ${SOLUTION_NAME}"
pac solution export \
  --name "${SOLUTION_NAME}" \
  --path "${TMP_ZIP}" \
  --managed true \
  --async true

echo "[S07] 源码化（unpack）-> ${SRC_DIR}"
mkdir -p "${SRC_DIR}"
pac solution unpack \
  --zipfile "${TMP_ZIP}" \
  --folder "${SRC_DIR}" \
  --packagetype Managed

echo "[S07] 提交到 Git"
git add "${SRC_DIR}"
git commit -m "feat(S07): export ${SOLUTION_NAME} managed [DAF]" || echo "(无变更)"

echo "[S07] 完成。部署到 UAT 走 Azure DevOps pipeline 或: pac solution import --path ${TMP_ZIP}"
