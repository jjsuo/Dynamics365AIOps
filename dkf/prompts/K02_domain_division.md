# K02 — 业务领域划分（AI 辅助，人工关注）

## 目标
把 `.dkf/meta/K01_C_entity_topology.json` 里的实体，按 **业务语义**（不是命名前缀）
划分到 D365 模块或自定义业务域，形成 DDD 风格的界限上下文。

## 输入
- `.dkf/meta/K01_C_entity_topology.json`（实体 + 关系）
- `.dkf/meta/K01_A_entry_points.json`（插件/Custom API 入口）
- `.dkf/meta/K01_P_processes.json`（流程）
- 领域专家清单（人工提供：本项目有哪些业务模块）

## 划分粒度（参考 VKF：分 5 个粒度，避免一刀切）
1. 标准模块域：Sales / Customer Service / Field Service / Marketing
2. 自定义业务域：按客户业务（如"合同管理""备件""派工"）
3. 共享/主数据域：account、contact、product 等被多域引用的
4. 集成域：纯对接外部系统的实体
5. unclassified：暂时无法归类的，留给 K03 人工确认

## 输出
写入 `.dkf/domains/K02_domains.json`：
```json
{ "domains": [
  { "name": "合同管理", "type": "custom",
    "entities": ["new_contract","new_contractline"],
    "key_processes": ["合同审批(BPF)"], "confidence": "high" }
]}
```
> ⚠️ 每个实体只归一个主域；被多域引用的标主域 + references。低置信度标 `medium`，交 K03。
