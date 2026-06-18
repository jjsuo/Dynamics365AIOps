# S01 — 详细设计 prompt

## 前置：加载 FDD/<id>.md + SDD/<module>.md + 对应 .dkf/skills/<domain>.md
## 任务
基于 FDD/SDD 出可直接照着配/写的详细设计，写入 `design/<module>.md`：
1. **实体 schema**：每个实体的字段（名/类型/必填/OptionSet）、关系、备用键
2. **表单/视图**：要改哪些表单、加哪些视图
3. **BPF / business rule / flow**：逐个列出触发条件 + 逻辑
4. **安全角色矩阵**：实体 × 角色 的读写权限（复用 .dkf 已有角色优先）
5. **pro-code 接口**：若 Fit-Gap=定制，列 plugin 注册点(message+entity+stage) / PCF / Custom API 签名
> 复用检查：凡 .dkf/skills 里已有的实体/流程，标"复用"，不重复设计。
