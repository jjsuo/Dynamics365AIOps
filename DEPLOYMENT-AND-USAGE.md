# D365 AI 范式 — 部署与使用说明

> 照着本文从零搭起来并跑通一个真实需求。三层对应落地路线：
> **DKF**（懂系统）→ **DAF P 阶段**（需求→Fit-Gap→FDD）→ **协作层 + S/T**（飞书话题 + 构建部署）。

---

## 一、先看一眼：你要准备什么

| 项 | 用途 | 必需性 |
|---|---|---|
| Python 3.8+ | 跑 DKF 扫描器 / 飞书脚本 | 必需 |
| Power Platform CLI (`pac`) | S07 solution 导出/部署 | 第三层需要 |
| Git（或 Azure DevOps） | 需求池 Hub / 解决方案仓 / 知识仓 | 必需 |
| Entra ID 应用注册 | DKF 只读访问 Dataverse | 第一层必需 |
| 飞书企业自建应用 | 拉需求文档 + 发门禁卡片 | 第二/三层需要 |
| 一个 D365 环境 | 被扫描 / 被部署 | 必需 |

---

## 二、安装

```bash
# 解压本项目后
cd d365-ai-paradigm

# DKF 扫描器
cd dkf && pip install -r requirements.txt && cd ..

# pac CLI（第三层 S07 用）
dotnet tool install --global Microsoft.PowerApps.CLI.Tool
```

---

## 三、配置（一次性）

### 3.1 Dataverse 只读访问（第一层 DKF）
1. **Entra ID → 应用注册 → 新注册**，记下 `tenant_id`、`client_id`。
2. **证书和密码 → 新建客户端密码**，记下密钥。
3. **Power Platform 管理中心 → 目标环境 → 设置 → 用户+权限 → 应用程序用户 → 新建**，选上面的应用。
4. 自建安全角色 `DKF Reader`，**只给读权限**（实体定义、roles/teams/businessunits、workflows、sdkmessageprocessingsteps、pluginassemblies、customapis、webresourceset、solutions），赋给该应用用户。
5. 填配置：
   ```bash
   cd dkf
   cp config.example.yaml config.yaml      # 填 resource_url / tenant_id / client_id
   export DKF_CLIENT_SECRET='你的密钥'       # 密钥走环境变量，不进 Git
   ```

### 3.2 飞书应用（第二/三层）
1. **飞书开放平台 → 创建企业自建应用**，拿 `app_id` / `app_secret`。
2. 开通权限：`docx:document:readonly`（读需求文档）、`im:message:send`（发门禁卡片）。
3. 把应用**加为需求文档协作者**，并**把机器人拉进工作台群**。
4. 设置环境变量：
   ```bash
   export FEISHU_APP_ID='cli_xxx'
   export FEISHU_APP_SECRET='xxx'
   ```
   > 国际版 Lark：把脚本里的 `BASE` 改成 `https://open.larksuite.com`。

### 3.3 仓库（按需求建）
- **需求池 Hub** 仓：放 `requirements/ fit-gap/ FDD/ SDD/ streams/ decisions/`
- **知识仓**：放 DKF 产出的 `.dkf/`（按客户保密要求控制访问）
- **解决方案仓**：每个交付流一个，放 `solutions/<name>/`（pac 源码化）

---

## 四、三层怎么用

### 第一层 DKF — 让 AI 懂系统
```bash
cd dkf
python -m dkf.cli check                # 连通性自检：调 WhoAmI，确认认证通（先跑这个）
python -m dkf.cli scan                 # K01 扫元数据 -> .dkf/meta/
python -m dkf.cli domains              # K02 草稿（前缀初分）
#  用 prompts/K02_domain_division.md 让 AI 按业务语义重划 -> .dkf/domains/K02_domains.json
#  人工 K03 确认 -> .dkf/domains/K03_confirmed.json   （prompts/K03_boundary_confirm.md）
python -m dkf.cli k04                  # K04 自动生成领域知识骨架 -> .dkf/skills/
python -m dkf.cli k04 --with-attributes  # （可选）联网把每个实体的自定义字段也填进去
#  用 prompts/K04_domain_knowledge.md 让 AI 补 ✍️ 段（域概述/坑点）
python -m dkf.cli index                # K07 构建系统地图 -> .dkf/index/system_map.md
```
**验收**：问 AI "合同到期逻辑在哪实现的"，它能根据 `.dkf/index` 指到正确实体/流程/插件。

### 第二层 DAF P 阶段 — 需求→Fit-Gap→FDD
在 AI 编码 agent（Claude Code / Copilot）里执行 `daf/daf_starter.md`，按菜单走 P01→P06：
```bash
# P01 先把飞书需求文档拉成文本
python daf/feishu/parse_feishu_doc.py --doc <document_id> --out req.txt
```
- **P03 Fit-Gap 是强制人工门禁**：AI 按 `templates/fit-gap.md` 给四象限建议，功能顾问/架构师拍板。
- 产物全部提交进需求池 Hub。

### 第三层 协作层 + S/T — 飞书话题 + 构建部署
```bash
# 阶段到门禁时，往模块话题发卡片，等异步放行
python collab/notify_feishu.py --chat <chat_id> --module 合同管理 --stage P03 \
    --summary "Fit-Gap=配置；FDD 已出，待放行" --artifacts FDD/REQ-001.md

# 构建：在解决方案仓里执行 daf/s_starter.md，走 S01→T01
# S07 打包部署
bash daf/scripts/solution_export.sh CustA_Core ./solutions/CustA_Core
```

---

## 五、端到端实战示例（一个需求走完全程）

**需求**：合同到期前 30 天自动提醒负责人，并把合同标记为"即将到期"。

| 阶段 | 动作 | 命令 / 产物 |
|---|---|---|
| **DKF** | 已对环境跑完 K01-K07，`.dkf/skills/合同管理.md` 里有 `new_contract` 的字段、流程、插件 | （前置已完成） |
| **P01** | 拉飞书需求文档 → AI 拆成 REQ-001 | `parse_feishu_doc.py --doc xxx`；产出 `requirements/REQ-001.md` |
| **P02** | 自动加载 `.dkf/skills/合同管理.md` | 上下文注入 |
| **P03** | AI 评估：标准无此能力 → 建议**配置**（Power Automate 定时流 + business rule）；出 FDD。复用 `.dkf` 里已有的 `new_contract` | `fit-gap/REQ-001.md` + `FDD/REQ-001.md` |
| 门禁 | 发卡片到"合同管理"话题，功能顾问手机回 `yes` | `notify_feishu.py --stage P03` |
| **P04/P05** | 归到 config 流（CustA_Core）；SDD 写明 `new_contract` 加 `new_expiry_status` 字段 + 定时流 | `streams/stream-mapping.json` + `SDD/合同管理.md` |
| **S01-S04** | 详设 → 在 dev 配字段+定时流+business rule → flow 测试 | `design/合同管理.md` + unmanaged solution + 配置工作簿 |
| **S06** | Solution Checker 无 High → code/配置评审 → 话题放行 | `notify_feishu.py --stage S06` |
| **S07** | `pac` 导出 managed + 源码化进 Git → 部署 UAT | `solution_export.sh CustA_Core` |
| **T01** | 按 P01 验收标准跑 UAT：造一个 29 天后到期的合同，验证提醒+标记 | 测试报告；业务方话题签核 |

走完一遍，你得到的不只是这个功能，还有：一条可复用的 `.dkf/skills/合同管理.md`、一份标准 FDD、一个 Fit-Gap 决策记录、一段飞书话题里的决策留痕——**这些就是不随人员流动流失的项目资产**。

---

## 六、日常命令速查

```bash
# DKF
python -m dkf.cli scan|domains|k04|index [--out .dkf] [--with-attributes]

# 飞书需求
python daf/feishu/parse_feishu_doc.py --doc <document_id> --out req.txt

# 门禁卡片
python collab/notify_feishu.py --chat <chat_id>|--reply <root_msg_id> \
    --module <名> --stage <P03|P05|S06|S07|T01> --summary "..." --artifacts a.md b.md

# 打包部署
bash daf/scripts/solution_export.sh <SolutionUniqueName> [src_dir]
```

---

## 七、排错 FAQ

| 现象 | 原因 / 解法 |
|---|---|
| `check`/`scan` 401 Unauthorized | secret 错/过期，或 tenant_id/client_id 填错 |
| `check`/`scan` 403 Forbidden | 应用用户没加进环境，或没赋读权限角色 |
| DKF scan 某实体显示名为空 | 不同环境本地化标签结构略有差异，看 `k01_scan.py` 的 display 取值那行，按你环境微调 |
| scan 量太大/慢 | `config.yaml` 设 `custom_only: true`，先只扫自定义实体 |
| 飞书取文档 99991663/权限错 | 没开 `docx:document:readonly` / 应用未加为文档协作者 |
| 飞书发卡片 230002 | 机器人没入群 / 没开 `im:message:send` |
| 飞书卡片按钮点击 200340 | 按钮回调需额外配事件回调 URL（增量 2）；MVP 用回复 `yes` 放行即可 |
| pac 命令找不到 | `dotnet tool install --global Microsoft.PowerApps.CLI.Tool`，确保在 PATH |

---

## 八、安全与边界
- DKF 全程**只读** Dataverse，最小权限，绝不写数据。
- 所有密钥（`client_secret` / `app_secret`）走环境变量；`config.yaml` 和含敏感元数据的 `.dkf/` 按需进 `.gitignore`。
- 飞书应用只开"读文档 + 发消息"，不开多余 scope。
- `.dkf/` 可能含客户业务信息，知识仓访问权限按客户保密要求控制。
