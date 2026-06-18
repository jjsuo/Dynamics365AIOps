# D365 AI 规范化交付范式 — 落地实现

基于小米 VAF/VKF/eight-claw 理念，为 D365 CE + Power Platform 小团队做的 AI 规范化交付范式。

## 三层
- **dkf/** — 第一层 DKF：知识库扫描器。扫 Dataverse 元数据 → 可检索"系统地图"，让 AI 先懂现有系统。
  - `scan`(K01) → `domains`(K02) → 人工 K03 → `k04` 半自动领域知识骨架 → `index`(K07)
- **daf/** — 第二层 DAF：P 阶段（需求→Fit-Gap→FDD）+ S/T 阶段（构建→部署→UAT）。
  - `daf_starter.md`（P 阶段入口）/ `s_starter.md`（S/T 入口）/ 模板 / prompt / 飞书需求解析 / pac 部署脚本
- **collab/** — 第三层：飞书协作层。话题=并行最小治理单元，门禁卡片异步放行。

## 跨 agent 编排层（process/ + bin/daf）⭐
流程不再绑定某个 agent。**单一真相源 = `process/manifest.yaml`**（声明所有 track/phase/门控/产物），
`bin/daf` 是中立驱动，各 agent 的入口文件由 `daf sync` **从 manifest 生成**——改流程只改 manifest 一处。

```bash
python3 bin/daf list            # 菜单：K 知识 / P 设计 / S·T 构建测试
python3 bin/daf show P03        # 某步的输入/产物/门控 + prompt 全文或要跑的命令
python3 bin/daf sync            # 生成/刷新 AGENTS.md · .claude/commands · .kiro/steering · copilot
```

任何 agent 只需「读 markdown + 跑 shell」即可一致执行。**分发与更新见 [DISTRIBUTION.md](DISTRIBUTION.md)**
（别人一行 `install.sh` 装到自己仓；你升 `manifest.version` 打 tag，他们一行 `--update`）。

## 标准化边界（贡献须知 ⚠️）
本仓是**通用框架**，不是某个客户项目。维护时严守"框架 / 项目数据"分离：

- **框架代码与模板**（`dkf/dkf/*.py`、`daf/*.md`、`daf/templates/`、`daf/prompts/`、`collab/*.py`）：**禁止出现任何项目特定内容**——不写死客户名/实体名/字段名/外部系统名/环境 URL（如 ❌ 天眼查、SAP、Vyung、华创、`nvt_`、具体 org 地址）。需要这类值时，从**数据/配置推导**或留占位（如从环境变量名结构化推导外部系统名，而非关键词硬匹配）。
- **项目数据**只许待在：`dkf/config.yaml`（gitignore）、`.dkf/`（扫描产物）、`deliverables/`（需求产物）、`code/`（生成代码）、`solutions/`（解决方案包）。
- 文档里的示例（如 DEPLOYMENT 的"合同到期提醒"）仅作演示，**框架代码不得依赖**它们。
- 新增扫描器/生成器前自检：`grep -rniE '<客户特征词>' dkf/dkf daf` 应为空。

## 文档
- **DEPLOYMENT-AND-USAGE.md** — 部署与使用 runbook（含端到端实战示例）⭐ 从这里开始
- **IMPLEMENTATION-PLAN.md** — 第 1+2 步落地方案 + MVP 时间盒
- 《D365-AI规范化交付范式》— 范式整体设计（三层架构、原则）

## 快速开始

### 0. 先离线验证（零云端，先判断有没有用）⭐
```bash
bash validate.sh    # 用 samples/ 的 mock 数据跑一遍，直接看产出
```
觉得产出对你的 AI agent 有用，再往下做云端设置。

### 1. 真实使用
```bash
cd dkf && pip install -r requirements.txt
cp config.example.yaml config.yaml && export DKF_CLIENT_SECRET='...'
python -m dkf.cli scan && python -m dkf.cli index
# 详见 DEPLOYMENT-AND-USAGE.md
```
