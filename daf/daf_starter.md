# @daf_starter — DAF P 阶段统一入口

> 对齐 VAF 的 `@vaf_starter.md`。在你的 AI 编码 agent（Claude Code / Copilot）里执行本文件，
> 它会渲染菜单、做阶段门控、在每个放行点等你决策。
>
> **阶段门控**：P01 未放行，P02 锁定；依此类推。多流并行后在 P06 汇合。
> **放行约定**：`yes` 放行进入下一步 · `e` 与 AI 继续修改当前产物。
> **自动提交**：每步产物提交到需求池 Hub，规范 `feat(P03): Fit-Gap & FDD [DAF]`。

---

## 菜单

```
需求项目：<project-name>
─────────────────────────────────────────────
  P01  需求采集（飞书需求文档 → 结构化清单）   [待执行]
  P02  知识加载（DKF 知识仓 + 标准能力）        [🔒 锁定]
  P03  Fit-Gap & FDD 评审                       [🔒 锁定]  ← 强制人工放行
  P04  方案拆解（配置/pro-code/集成/迁移 流）   [🔒 锁定]
  P05  概要设计 SDD                              [🔒 锁定]  ← 强制人工放行
  P06  协调中心（多流汇合门禁，仅多流时启用）   [🔒 锁定]
─────────────────────────────────────────────
```

## 各步驱动的 prompt 与产物

| 步骤 | prompt | 输入 | 产物（提交到 Hub） |
|---|---|---|---|
| P01 | `prompts/P01_intake.md` | 飞书需求文档 / BRD | `requirements/<id>.md`（结构化需求） |
| P02 | （自动）加载 `.dkf/index/system_map.md` + `.dkf/skills/` | DKF 知识仓 | 上下文注入，无独立产物 |
| P03 | `prompts/P03_fitgap.md` | P01 需求 + P02 知识 | `fit-gap/<id>.md` + `FDD/<id>.md` |
| P04 | `prompts/P04_split.md` | FDD | `streams/stream-mapping.json` |
| P05 | `prompts/P05_sdd.md` | FDD + 拆解结果 | `SDD/<module>.md`（数据/安全/集成/环境） |
| P06 | （门禁脚本） | 各流就绪状态 | `P06_gate.md`（汇合评审记录） |

## 产物落地约定（v2，按需求分类归档）
每条需求的产物**集中放到自己的目录**，新需求 = 新文件夹，**只增不覆盖老的**：
```
deliverables/<module>/
  fit-gap.md  FDD.md  build-record.md   # 模块级"总览/索引"(汇总表 + 链到各 REQ)
  SDD.md  stream-mapping.json  P06_gate.md  集成设计.md  安全矩阵   # 模块级共享
  <REQ-ID>/
    requirement.md     # P01
    fit-gap.md         # P03（按需求）
    FDD.md             # P03（按需求）
    build-record.md    # S 阶段实建记录（按需求 + 迭代记录，见下）
    design.md          # S01 详设（仅复杂需求才建，不造空壳）
```

### 粒度三档（内容驱动）
| 档 | 产物 | 规则 |
|---|---|---|
| 永远按需求 | requirement · fit-gap · FDD · **build-record** | 每 REQ 一份。build-record 含**迭代记录**(v1/v2…)，需求频繁变更时各自留痕，新需求不覆盖老的 |
| 永远模块级 | SDD(数据模型/安全/ALM聚合) · stream-mapping · P06_gate · 集成设计 · 安全矩阵 | 天生跨需求，拆开会割裂数据模型；增量更新，不重写整篇 |
| 弹性 | design(S01详设) | 需求大才建独立一份；小需求并入 FDD，不造空壳 |

- 模块级 fit-gap/FDD/build-record 是**总览索引**（象限汇总表、聚合数据模型、各 REQ 状态 + 链接）。
- 新需求：建 `<REQ>/` 放它的 requirement/fit-gap/FDD/build-record；模块级总览**追加一行**链接。
- AI 与人都按 `deliverables/<module>/<REQ>/` 定位"这条需求做了哪些步骤、改了几次"。

## 代码落地约定
- DAF 生成的所有代码放仓库根 `code/<SolutionUniqueName>/`（如 `code/<Prefix>_<Module>_Plugins/`）。
- 代码遵循 `templates/code-standards.md`（**可后期修改**，改完后续生成按新规范）。
- Mac 上的编译/签名/注册照 `MAC-NOTES.md` 与 `code/README-Mac插件工作流.md`。

## 飞书通知约定（即时 + 长操作进度）
- **门禁**(P03/P05/S06/S07/T01)：发门禁卡片，等话题里 `yes` 异步放行（脚本可轮询话题回复自动接力）。
- **长操作**（建实体/字段、扫描、导出部署等耗时步）：**开始发"进行中"、完成发"完成"、卡住发"阻塞"**：
  ```bash
  python collab/notify_feishu.py --chat <id> --module <名> --status in_progress --step "S03 建实体字段" --detail "正在建17实体…"
  # …执行…
  python collab/notify_feishu.py --chat <id> --module <名> --status done --step "S03 建实体字段" --detail "17实体/189字段 完成"
  ```
- 项目开始即固定 chat_id，避免门禁时无处可发。

## 状态机（沿用 VAF）
`locked🔒 → unlocked → executing → pending_review → approved`

## 环境要求
- Git（需求池 Hub 仓已 clone）
- 已跑过第一步 DKF：`.dkf/index/` 和 `.dkf/skills/` 存在（P02 依赖）
- 飞书 app 凭据（P01 拉文档用）或本地导出的需求 MD
