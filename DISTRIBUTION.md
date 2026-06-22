# 分发与更新 — 让别人在任意 agent 里快速用上这套范式

核心思路：**框架 / 项目数据 严格分离**（见 README「标准化边界」）。因为分离干净，所以
「安装」和「更新」都只是——**刷新框架那一层，绝不碰对方的项目数据**。

```
对方的项目仓/
├── .daf-framework/        ← 框架副本（git submodule，钉死版本）= 只读，可整体替换
├── AGENTS.md              ← daf sync 生成（Codex / Cursor / 通用）
├── CLAUDE.md              ← @AGENTS.md（Claude Code）
├── .claude/commands/daf.md   ← Claude Code 斜杠命令
├── .kiro/steering/daf.md     ← Kiro
├── .github/copilot-instructions.md  ← Copilot
├── daf.lock              ← 记录所用框架版本（可复现）
└── deliverables/ code/ .dkf/ dkf/config.yaml   ← 他的项目数据（安装/更新都不动）
```

## 给别人的「快速开始」（一行）

> 在他**自己项目仓的根目录**执行：

```bash
curl -fsSL https://raw.githubusercontent.com/jjsuo/Dynamics365AIOps/main/install.sh | bash
```

它会：① 把框架作为 submodule 钉进 `.daf-framework/`；② 跑 `daf sync` 生成适配器
+ 跨平台启动器（`daf` / `daf.cmd`）；③ 写 `daf.lock`。

钉死某个版本（推荐生产用）：`DAF_REF=v0.3.0 bash install.sh`。

## 新电脑上的完整流程（DKF 先就位，之后全程 DAF）

装完后，**`daf` 不是系统命令**，是项目根的启动器：Windows cmd 直接 `daf …`，macOS/Linux/git-bash 用 `./daf …`（self-dev 仓用 `python3 bin/daf …`）。

```bash
daf doctor            # 自检：python / dkf 配置 / 知识库 是否就位，告诉你下一步
# 1) 让 DKF 知识库就位（每台新机器/换环境做一次）
cp .daf-framework/dkf/config.example.yaml dkf/config.yaml   # 填环境 URL/tenant/client
export DKF_CLIENT_SECRET='...'                              # 凭据走环境变量
daf knowledge         # 自动跑 K01 扫描 → K02 划域 → K04 骨架 → K07 索引 → 写 .dkf/
# 2) 之后每次只跟 agent 说需求即可
```

第 2 步**不用你记命令**：Codex 自动读 `AGENTS.md`、Claude Code 读 `CLAUDE.md`，里面写死了
「任何交付/需求/构建请求都走 DAF：先 `daf doctor`/`daf list`，再 `daf show <步骤>` 按步执行，门控停」。
所以你直接说"按 DAF 帮我做这条需求"，agent 就会自己 `daf list` → 从 P01 走起。

## 给别人的「快速更新」（一行）

```bash
bash .daf-framework/install.sh --update      # 或： python3 .daf-framework/bin/daf update
```

它 `git pull` 框架副本到最新，然后**重新 `daf sync`**——只重写 `AGENTS.md` 这类生成物，
他的 `deliverables/`、`code/`、`.dkf/`、`config.yaml` 一律不动。更新完看 `daf.lock` 知道版本。

## 你（维护者）发布更新的姿势

1. 改流程：**只改 `process/manifest.yaml` / `daf/prompts/` / `daf/templates/`**（单一真相源）。
2. 升版本号：`process/manifest.yaml` 的 `framework.version`。
3. 打 tag：`git tag v0.3.0 && git push --tags`。
4. 通知用户：跑一行 `--update` 即可。**他们不必懂你改了什么**——适配器自动按新 manifest 重生成。

> 为什么这样跨 agent 还能稳：适配器是「生成物」不是「手维护物」。新增一种 agent 支持，
> 只在 `bin/daf` 的 `cmd_sync` 里加一个输出目标，所有用户 `--update` 后白拿。

## 三种分发档位（按对方习惯选）

| 档 | 机制 | 更新方式 | 适合 |
|---|---|---|---|
| **submodule**（默认） | `.daf-framework/` 钉 commit | `install.sh --update` | 想复现、想锁版本的团队 |
| vendored 拷贝 | 直接 clone 到 `.daf-framework/` | 同上（走 git pull） | 不想用 submodule 的人 |
| 全局 CLI | `pipx install` 本仓（dkf 已是 pip 包） | `pipx upgrade` + `daf sync` | 多项目共用一份框架 |

三档的共同点：流程逻辑都在 manifest，适配器都靠 `daf sync` 生成，所以换档不换行为。
