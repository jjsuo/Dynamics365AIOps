<!-- 本文件由 `daf sync` 从 process/manifest.yaml 生成，勿手改；改流程改 manifest。framework v0.2.0 -->

# d365-ai-paradigm — AI 交付范式入口

本仓采用 **D365 AI 规范化交付范式**（DKF 知识库 + DAF 交付流程）。任何 AI agent 按下述方式执行，行为一致。

## 你（agent）的工作方式
1. 流程的单一真相源是 `process/manifest.yaml`。**不要凭记忆推断流程**，用命令查：
   - `python3 bin/daf list` — 看所有 track（K 知识 / P 设计 / S·T 构建测试）与步骤
   - `python3 bin/daf show <步骤ID>` — 看某步的输入/产物/门控，以及该步的 prompt 全文或要跑的命令
2. **K track（DKF）是确定性 CLI**，直接按 `show` 给的 `run` 命令执行即可。
3. **P / S track（DAF）是判断类**，按 `show` 打印的 prompt 执行，产出落到 `deliverables/` 或 `code/`。
4. **门控步骤**（标 `人工放行`）：产出后停下等用户 `yes` 放行 / `e` 继续改，不要自行越过。
5. 每步产物提交：`每步产物自动提交，规范 feat(<PHASE>): <说明> [DAF]`

## 边界（重要）
- 框架文件（process/, dkf/dkf/, daf/prompts/, daf/templates/, daf/scripts/, collab/）只读地遵循，不要把客户名/实体名/外部系统名写进去。
- 项目产物只写到：dkf/config.yaml, .dkf/, deliverables/, code/, solutions/。

## 更新框架
本范式有更新时：`python3 bin/daf update`（只刷新框架文件，不动你的项目数据）。
