# 功能设计文档 FDD 模板（P03 产物，写入 Hub: FDD/<id>.md）

## 1. 需求概述
- 需求 ID / 标题 / 来源 / 优先级
- 业务背景（1-2 句）

## 2. Fit-Gap 结论
- 象限：配置 / 定制 / 集成
- 复用的 DKF 已有资产（指向 .dkf/skills/）

## 3. 功能设计
### 3.1 数据模型变更
| 实体 | 变更 | 字段/关系 | 说明 |
|---|---|---|---|
| new_contract | 改 | new_expiry_status (OptionSet) | 即将到期标记 |

### 3.2 业务流程
- 触发：Power Automate 定时流（每日）
- 逻辑：查到期前 30 天的合同 → 发提醒 → 更新状态
- 涉及 BPF / business rule：列出

### 3.3 安全与可见性
- 哪些角色受影响（指向 .dkf/meta/K01_G_security.json）

### 3.4 集成（如有）
- 接口、连接器、数据流向

## 4. 验收标准
（直接引用 P01 的 acceptance_criteria）

## 5. 未决问题
（引用 P01 open_questions，标注解决状态）
