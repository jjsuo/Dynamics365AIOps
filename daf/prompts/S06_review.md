# S06 — 评审门禁 prompt（飞书异步放行）

## 自动门禁
1. 跑 **Solution Checker**（pac solution check）→ 必须无 High 级问题
2. pro-code 跑单测（S04 的 FakeXrmEasy / flow test）

## 人工评审
- 配置审查：对照配置工作簿，确认无多余/遗漏
- code review：plugin/PCF 代码评审
- ALM 检查：solution 依赖、托管属性、环境变量是否就绪

## 放行
通过后用 `collab/notify_feishu.py --stage S06` 发门禁卡片到话题，等放行 → 解锁 S07。
