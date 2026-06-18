# P01 结构化需求模板（每条需求一份，写入 Hub: requirements/<id>.md）

```yaml
id: REQ-001
title: 合同到期自动提醒
module: 合同管理            # 对应 DKF 的领域，便于 P02 精准加载知识
source: 飞书需求文档 §3.2   # 溯源，便于回查
priority: 高
requirement: |
  合同到期前 30 天，系统自动给负责人发提醒，并在合同上标记"即将到期"。
acceptance_criteria:        # 验收标准，P03 Fit-Gap 和 T01 测试都引用
  - 到期前 30 天触发
  - 提醒发给合同 owner
  - 合同状态字段更新为"即将到期"
open_questions:             # P01 解析时 AI 识别出的待澄清点
  - 提醒渠道是邮件还是站内通知？
```
