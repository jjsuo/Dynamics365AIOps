# DAF/DKF 在 macOS 上的经验备注

> 实战(arm64 macOS + dotnet 10)沉淀的坑与解法。DAF/S 阶段在 mac 上跑时照此办。

## 1. pac CLI 在 mac 上崩溃 → 改用 Web API
- 现象：pac 2.8.1 每次执行前的"自动 OS 登录"调 MSAL broker，mac 无 broker → NullReferenceException，连 `pac auth list` 都崩。
- 解法：**solution 导出/导入、组件操作全走 Dataverse Web API**：
  - 导出 managed：`ExportSolution`(Managed=true) → base64 → 写 zip。
  - 导入：`ImportSolution`。
  - 建实体/字段/关系/角色/Custom API：直接 POST `EntityDefinitions`/`RelationshipDefinitions`/`roles`/`customapis` 等。
- 凭据复用 dkf/config.yaml 的 service principal（client credentials 拿 token）。

## 2. 元数据写操作的坑
- 整数列**不支持列默认值**（IntegerAttributeMetadata 无 DefaultValue）→ "创建赋默认值"改用业务规则/插件。
- `@odata.bind` 导航属性名大小写敏感：customapi 的 lookup 是 `CustomAPIId`（PascalCase），不是 `customapiid`。
- 选 `clientdata`/`xaml` 等大字段时显式 `$select` 反而返回空，取整条记录才有；`$filter` 里放 `type eq 1` 偶发返回空 → 改客户端过滤。
- 加字段到标准实体(account/contact)用 `MSCRM.SolutionUniqueName` 头归进解决方案。
- 长批量(几百次元数据 POST)会偶发 ReadTimeout → 脚本要可幂等重跑、断点续建。

## 3. 插件编译（不需要 Windows 虚拟机）
- 插件只在 Dataverse 沙箱运行，本机**只编译不运行** → 用 `Microsoft.NETFramework.ReferenceAssemblies` 跨平台编 net462。
- 强名 .snk：mac 无 `sn.exe`，用 Python `cryptography` 造 RSA → 写 CAPI PRIVATEKEYBLOB(2048 位=1172 字节)。
- 注册走 Web API：pluginassembly(base64) + plugintype + 绑 Custom API。
- 详见 code/README-Mac插件工作流.md。

## 4. 环境
- dotnet 用 brew 装：`brew install dotnet`，需 `export DOTNET_ROOT="/opt/homebrew/opt/dotnet/libexec"` 和 `PATH` 加 `~/.dotnet/tools`。
- DKF CLI 必须传 `--out`（绝对路径），否则从 dkf/ 目录跑会写到 `dkf/.dkf/`、与根 `.dkf/` 分裂。
