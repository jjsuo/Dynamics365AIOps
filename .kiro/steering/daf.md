<!-- 本文件由 `daf sync` 从 process/manifest.yaml 生成，勿手改；改流程改 manifest。framework v0.3.0 -->

# d365-ai-paradigm — AI 交付范式入口

本仓采用 **D365 AI 规范化交付范式**（DKF 知识库 + DAF 交付流程）。
**凡是交付 / 需求 / 构建 / 分析类的请求，都必须走 DAF 流程，不要绕过。** 任何 AI agent 按下述执行，行为一致。

> 运行约定：下文 `daf` = 项目根的启动器。Windows cmd 直接 `daf …`；macOS/Linux/git-bash 用 `./daf …`。

## 0. 首次 / 新机器先做（让 DKF 知识库就位）
DAF 的 P 阶段依赖 DKF 知识。开工前先确认 `.dkf/index/system_map.md` 是否存在（或跑 `daf doctor` 自检）：
- **不存在** → 先建知识库：从 `dkf/config.example.yaml` 复制出 `dkf/config.yaml` 填环境与凭据，再 `daf knowledge`（自动跑 K01 扫描 → K02 划域 → K04 骨架 → K07 索引）。
- **已存在** → 直接进下一节。

## 1. 每次请求怎么走
1. 流程真相源是 `process/manifest.yaml`，**别凭记忆**，用命令查：
   - `daf list` — 看 track（K 知识 / P 设计 / S·T 构建测试）与步骤
   - `daf show <步骤ID>` — 某步的输入/产物/门控 + prompt 全文或要跑的命令
2. 判断当前该到哪步（没有知识库就先回第 0 步），从该步起按 `show` 执行：
   - **K track** = 确定性 CLI，直接跑 `run` 命令
   - **P / S track** = 判断类，按 prompt 产出到 `deliverables/` 或 `code/`
3. **门控步骤**（标 `人工放行`）：产出后停下等用户 `yes` 放行 / `e` 改，**不要自行越过**。
4. 每步产物提交：`每步产物自动提交，规范 feat(<PHASE>): <说明> [DAF]`

## 边界（重要）
- 框架文件（process/, dkf/dkf/, daf/prompts/, daf/templates/, daf/scripts/, collab/）只读地遵循，不要把客户名/实体名/外部系统名写进去。
- 项目产物只写到：dkf/config.yaml, .dkf/, deliverables/, code/, solutions/。

## 更新框架
`daf update`（git pull 框架 + 重新生成适配器，只刷新框架文件，不动你的项目数据）。
