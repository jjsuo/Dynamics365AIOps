# P05 — 概要设计 SDD prompt（强制人工放行）

## 任务
基于 FDD + P04 拆解结果，产出模块级 SDD，写入 Hub: SDD/<module>.md。

## 必含四块
1. **数据模型**：新增/变更实体、字段、关系、键（汇总所有 FDD 的 §3.1）
2. **安全模型**：BU / Team / 安全角色矩阵（对照 .dkf/meta/K01_G_security.json，复用现有角色优先）
3. **集成架构**：所有"集成"象限需求的接口、连接器、数据流向
4. **环境策略**：dev → test(UAT) → prod 的 solution 切分与 ALM 路径

## 放行
架构师放行后 commit `feat(P05): SDD [DAF]`，进入 P06（多流）或直接 S 阶段。
