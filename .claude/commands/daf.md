---
description: 按 D365 AI 交付范式执行下一步（DKF/DAF）
---

你正在一个采用 D365 AI 交付范式的仓库里。流程真相源是 manifest，**用命令查，别凭记忆**：

1. 先 `python3 bin/daf list` 了解当前可做的 track 与步骤。
2. 用户指定步骤（或你判断的下一步）→ `python3 bin/daf show <步骤ID>` 拿到该步的输入/产物/门控与 prompt/命令。
3. 严格按 show 的内容执行：K track 跑 run 命令；P/S track 按 prompt 产出到 deliverables/ 或 code/。
4. 门控步骤产出后停下等用户 `yes`/`e`，别自行越过。
5. 提交：每步产物自动提交，规范 feat(<PHASE>): <说明> [DAF]

用户参数：$ARGUMENTS（可能是步骤ID，如 P03；为空就先 list 再问用户从哪步开始）。
