# P03 — Fit-Gap & FDD prompt（强制人工放行）

## 前置
P02 已把 .dkf/index/system_map.md 和相关 .dkf/skills/<module>.md 注入上下文。

## 任务（逐条需求）
1. **标准能力评估**：基于 D365 标准 + DKF 已有定制，判断现状能否满足
2. **四象限判定**：按 templates/fit-gap.md 给出 标准/配置/定制/集成 建议 + 理由
3. **复用检查**：在 .dkf/skills/ 里找可复用的已有实体/流程，写进 FDD §2
4. 产出 fit-gap/<id>.md + FDD/<id>.md

## 关键约束
- AI 只给**建议**，最终象限由功能顾问/架构师放行（这是门禁）
- 涉及"定制"或"集成"象限时，必须列风险 + 前置依赖
- 不要凭空假设标准能力——不确定就标 open_question，别编

## 放行
用户对每条需求的象限 yes 放行后，commit `feat(P03): Fit-Gap & FDD [DAF]`，解锁 P04。
