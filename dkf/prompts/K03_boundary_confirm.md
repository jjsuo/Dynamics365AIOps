# K03 — 边界确认（人工核心节点）

## 目标
人工审核 K02 的划分结果：
1. 确认 unclassified 实体的归属
2. 复核 confidence=medium 的条目
3. 处理跨域共享实体的主域归属

## 操作
直接编辑 `.dkf/domains/K02_domains.json`，把每条改成 `confidence: confirmed`。
有争议的，在该实体下加 `note` 说明为什么这么归。

## 产物
`.dkf/domains/K03_confirmed.json`（K02 的人工确认版，作为 K04 输入）
