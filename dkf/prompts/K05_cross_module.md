# K05 — 跨模块文档（仅 ≥2 域涉及时）

## 目标
描述跨领域的端到端业务链路，比如 Lead→Opportunity→Quote→Order 跨 Sales + 自定义计费域。

## 输入
- `.dkf/skills/*.md`（各域知识）
- `.dkf/meta/K01_C_entity_topology.json`（跨域关系）

## 产物（写入 .dkf/cross/<flow_name>.md）
- 链路图（实体 → 实体，标关系名）
- 每一跳由哪个流程/插件驱动（指向 meta）
- 跨域的状态流转与数据所有权

## 触发条件
该业务链路涉及 ≥2 个 K03 确认的领域时才生成；单域内的留在 K04。
