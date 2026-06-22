---
description: 按 D365 AI 交付范式执行下一步（DKF/DAF）
---

你在一个采用 D365 AI 交付范式的仓库里。**任何交付/需求/构建/分析请求都走 DAF**。
`daf` = 项目根启动器（Windows `daf`，mac/Linux `./daf`）。流程真相源是 manifest，**用命令查，别凭记忆**：

0. 先确认知识库就位：`daf doctor`。缺 `.dkf/` → 引导用户配 `dkf/config.yaml` 后 `daf knowledge`。
1. `daf list` 了解 track 与步骤。
2. 用户指定步骤（或你判断的下一步）→ `daf show <步骤ID>` 拿输入/产物/门控与 prompt/命令。
3. 严格按 show 执行：K track 跑 run 命令；P/S track 按 prompt 产出到 deliverables/ 或 code/。
4. 门控步骤产出后停下等用户 `yes`/`e`，别自行越过。
5. 提交：每步产物自动提交，规范 feat(<PHASE>): <说明> [DAF]

用户参数：$ARGUMENTS（可能是步骤ID，如 P03；为空就先 doctor + list 再问用户从哪步开始）。
