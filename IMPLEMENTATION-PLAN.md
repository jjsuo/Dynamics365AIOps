# D365 AI 范式落地实施方案（第一步 DKF + 第二步 DAF）

本方案对应《D365-AI规范化交付范式》的落地路线第 1、2 步。第 3 步（飞书协作层 + S/T）在前两步稳定后再做。

```
d365-ai-paradigm/
├── dkf/                第一步：知识库扫描器（可执行）
│   ├── dkf/            扫描器源码（auth/client/k01_scan/k07_index/cli）
│   ├── prompts/        K02-K05 AI 辅助步骤模板
│   ├── config.example.yaml
│   └── requirements.txt
└── daf/                第二步：P 阶段（统一入口 + 模板 + 飞书解析）
    ├── daf_starter.md  P 阶段统一入口菜单
    ├── templates/      需求/Fit-Gap/FDD 模板
    ├── prompts/        P01/P03/P05 prompt
    └── feishu/         飞书需求文档抓取脚本
```

---

## 第一步：DKF 知识库（让 AI 先懂你们的系统）

### 1. 前置准备（一次性，约半天）

**a) Entra ID 注册应用**
1. Entra ID → 应用注册 → 新注册（记下 `tenant_id`、`client_id`）
2. 证书和密码 → 新建客户端密码（记下 `client_secret`，只显示一次）

**b) Dataverse 加应用用户 + 只读角色**
1. Power Platform 管理中心 → 目标环境 → 设置 → 用户+权限 → 应用程序用户 → 新建，选上面注册的应用
2. 自建一个安全角色 `DKF Reader`，**只给读权限**：实体定义、安全表、workflow、sdkmessageprocessingstep、pluginassembly、customapi、webresource、solution 等系统表的 Read（组织级）
3. 把 `DKF Reader` 赋给该应用用户

> 这一步刻意只读、最小权限——扫描器永远不写 Dataverse。

**c) 安装**
```bash
cd dkf
pip install -r requirements.txt
cp config.example.yaml config.yaml   # 填 resource_url / tenant_id / client_id
export DKF_CLIENT_SECRET='你的密码'    # 密钥走环境变量，不进 Git
```

### 2. 执行顺序

| 步骤 | 命令 / 动作 | 性质 | 产物 |
|---|---|---|---|
| K01 | `python -m dkf.cli scan` | 自动 | `.dkf/meta/*.json`（实体/安全/流程/插件/集成入口） |
| K02 | `python -m dkf.cli domains` 生成草稿 → 用 `prompts/K02_domain_division.md` 让 AI 按业务语义重划 | AI + 人工 | `.dkf/domains/K02_domains.json` |
| K03 | 人工编辑确认领域归属（`prompts/K03_boundary_confirm.md`） | **人工** | `.dkf/domains/K03_confirmed.json` |
| K04 | 用 `prompts/K04_domain_knowledge.md` 逐域生成知识 Skill | AI + 人工审核 | `.dkf/skills/<domain>.md` |
| K05 | 跨域链路（仅 ≥2 域涉及时） | AI + 人工 | `.dkf/cross/<flow>.md` |
| K07 | `python -m dkf.cli index` | 自动 | `.dkf/index/system_map.md` + `entity_hooks.json` |

> 起步建议 `custom_only: true`，只扫自定义实体，量小、聚焦客户定制；摸顺后再放开标准实体。

### 3. 人工节点（不能省）
- **K03 边界确认**：领域划分对不对，直接决定 K04 知识质量。架构师必须过。
- **K04 审核**：AI 生成的领域知识要人工核一遍坑点和业务规则，避免"看似合理但不准"。

### 4. 验收标准
- AI 在 `.dkf/index/system_map.md` 里能看到"哪个实体被哪些插件/流程挂着"
- 随便问 AI 一个业务问题（"合同到期逻辑在哪实现的"），它能根据索引指到正确的实体/流程/插件，而不是瞎猜

---

## 第二步：DAF P 阶段（标准化"飞书需求 → Fit-Gap → FDD"）

### 1. 前置准备
- 第一步已完成：`.dkf/index/` 和 `.dkf/skills/` 存在（P02 依赖它们）
- 建一个 **需求池 Hub** Git 仓（放 requirements/ fit-gap/ FDD/ SDD/）
- 飞书需求文档抓取（可选，也可人工导出 MD）：
  1. 飞书开放平台建企业自建应用，拿 `app_id` / `app_secret`
  2. 开通 `docx:document:readonly` 权限
  3. 把应用加为需求文档协作者
  ```bash
  export FEISHU_APP_ID='cli_xxx'; export FEISHU_APP_SECRET='xxx'
  python daf/feishu/parse_feishu_doc.py --doc <document_id> --out req.txt
  ```

### 2. 执行顺序（在 AI 编码 agent 里跑 `@daf_starter.md`）

| 步骤 | 动作 | 性质 | 产物 |
|---|---|---|---|
| P01 | 飞书需求/BRD → 结构化需求清单 | AI + 人工放行 | `requirements/<id>.md` |
| P02 | 自动加载 DKF 索引 + 相关领域 skill | 自动 | 上下文注入 |
| P03 | 逐条需求做 Fit-Gap 四象限 + 出 FDD | AI 建议 + **人工拍板** | `fit-gap/<id>.md`、`FDD/<id>.md` |
| P04 | 拆成 配置/pro-code/集成/迁移 流 | AI + 人工 | `streams/stream-mapping.json` |
| P05 | 概要设计 SDD（数据/安全/集成/环境） | AI + **人工放行** | `SDD/<module>.md` |
| P06 | 多流汇合门禁（仅多流时） | 人工 | `P06_gate.md` |

### 3. 人工节点（强制门禁）
- **P03 Fit-Gap**：象限决策（标准/配置/定制/集成）由功能顾问/架构师拍板，AI 只给建议。这是整个范式价值最高、也最不能让 AI 自动放行的地方。
- **P05 SDD**：数据模型和安全模型一旦定了，后面所有 solution 都依赖它，架构师必须过。

### 4. 验收标准
- 一份飞书需求文档进去，出来的是：结构化需求清单 + 每条的 Fit-Gap 决策 + FDD，且 FDD 里能正确复用 DKF 已识别的既有资产（不重复造已有的实体/流程）

---

## 小团队 MVP 时间盒（参考，3-4 周）

| 周 | 目标 | 谁 |
|---|---|---|
| W1 | 搭好 Entra 应用 + DKF Reader 角色，跑通 K01 扫描（custom_only） | 架构师/技术顾问 |
| W2 | K02-K03 领域划分 + 确认，K04 生成 2-3 个核心域的知识 skill，K07 出索引 | 架构师 + 功能顾问 |
| W3 | 接第二步：建 Hub 仓 + 飞书抓取，拿 1 个真实需求文档跑通 P01→P03 | 功能顾问 |
| W4 | 补 P04-P05，回顾调优 prompt 模板，沉淀成团队 SOP | 全员 |

> **不要并行启动两步**。让 DKF（懂业务）先就位，DAF 才有可靠的知识底座——流程没问题但 AI 不懂业务，产出仍会偏差大。先把第一步的索引质量做扎实，第二步的 Fit-Gap 才准。

---

## 安全与边界须知
- 扫描器全程**只读** Dataverse，最小权限，不写任何数据。
- 所有密钥（client_secret / app_secret）走环境变量，`config.yaml` 和 `.dkf/`（如含敏感元数据）按需进 `.gitignore`。
- 飞书应用只开"读文档"权限，按需加协作者，不开多余 scope。
- `.dkf/` 里的元数据可能含客户业务信息，知识仓的访问权限按客户保密要求控制。
