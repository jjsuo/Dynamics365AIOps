# @s_starter — DAF S/T 阶段统一入口（构建实现 + 测试）

> 在解决方案仓里执行。前置：P 阶段已出 FDD/SDD，stream-mapping.json 已拆好流。
> 放行约定同 P 阶段：`yes` 放行 / `e` 改。门禁阶段(S06/S07/T01)经飞书话题异步放行。

## 菜单
```
解决方案：<solution-name>  流：<config|procode|integration|migration>
─────────────────────────────────────────────
  S01  详细设计（实体schema/表单/BPF/安全角色）   [待执行]
  S02  任务拆解（配置/开发/集成 任务）            [🔒]
  S03  配置&编码实现（dev 环境）                  [🔒]
  S04  单元/组件测试（FakeXrmEasy/flow test）     [🔒]
  S05  集成计划（API/连接器/虚拟表/数据迁移映射） [🔒]
  S06  评审门禁（Solution Checker + code review） [🔒]  ← 飞书门禁
  S07  打包部署（pac export managed → UAT）       [🔒]  ← 飞书门禁
  T01  端到端 / UAT 业务流程验收                  [🔒]  ← 飞书门禁
─────────────────────────────────────────────
```

## 各步 prompt / 脚本
| 步骤 | prompt / 脚本 | 产物 |
|---|---|---|
| S01 | `prompts/S01_detail_design.md` | `deliverables/<module>/<REQ>/design.md` |
| S03 | `prompts/S03_build.md` | unmanaged solution + 配置工作簿 + pro-code 源码(放 `code/<solution>/`) |
| S06 | `prompts/S06_review.md` + Solution Checker | 评审记录 |
| S07 | `scripts/solution_export.sh`（pac 不可用时走 Web API ExportSolution） | managed solution（导出 + 源码化进 Git） |
| T01 | `prompts/T01_uat.md` | 测试报告 + 缺陷回流 |

## 约定（v2，对齐 daf_starter）
- **代码**：一律放仓库根 `code/<SolutionUniqueName>/`，遵循 `templates/code-standards.md`（可后期改）。
- **产物**：S 阶段记录放 `deliverables/<module>/<REQ>/build-record.md`。
- **Mac 环境**：pac 崩 → solution 导出/导入/组件操作走 Dataverse Web API；插件 net462 跨平台编译+强名签名+Web API 注册，见 `MAC-NOTES.md`、`code/README-Mac插件工作流.md`。
- **飞书通知**：S03 建实体/字段、S07 导出部署等长操作，开始发 `--status in_progress`、完成发 `--status done`；门禁(S06/S07/T01)发门禁卡片等话题 `yes`。
- **代码逻辑回流 DKF**：S 阶段写完代码后跑 `python -m dkf.cli code --code-dir code`，把插件碰的实体/环境变量补进 `.dkf/meta/K09_code_logic.json`，并自动生成 **`.dkf/index/K09_code_flow.md` 代码流程图**(Mermaid)，让 DKF 知识与流程图跟上代码。
