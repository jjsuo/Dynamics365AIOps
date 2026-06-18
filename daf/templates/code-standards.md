# DAF 代码生成规范（可编辑）

> DAF 在 procode/集成流生成的代码遵循本规范。本文件**可由你后期修改**，
> 改完后续代码生成会按新规范走。生成代码统一放在仓库根 `code/<solution>/`。

## 1. 目录与命名
- 根目录：`code/`，按解决方案分子目录：`code/<SolutionUniqueName>/`（如 `code/<Prefix>_<Module>_Plugins/`）。
- 插件工程：`<Publisher>.<Module>.Plugins`。
- 一个 Custom API / 一个触发场景 = 一个插件类，文件名 = 类名。
- 共享逻辑放 `Helpers.cs`（读环境变量、HttpClient 等）。

## 2. 技术栈与编译（Mac 友好，见 MAC-NOTES.md）
- 目标框架 **net462**（Dataverse 沙箱要求），`dotnet build` 跨平台编译。
- 必用 NuGet：`Microsoft.NETFramework.ReferenceAssemblies`（让 Mac 能编 net462）、`Microsoft.CrmSdk.CoreAssemblies`。
- 出站 HTTP：`<Reference Include="System.Net.Http" />`（框架程序集，沙箱允许）。
- **强名签名**：`SignAssembly=true` + `<key>.snk`（一次性生成，提交进仓库）。

## 3. 插件编码约定
- 实现 `IPlugin.Execute`；从 `ctx.InputParameters` 读 Custom API 入参，写 `ctx.OutputParameters` 出参。
- 凭据/端点**一律走环境变量**（`Helpers.GetEnvVar`），不硬编码、不进 Git。
- 异常：业务失败抛 `InvalidPluginExecutionException`（带可读消息）；用 `ITracingService` 记跟踪。
- 外部调用失败要可重试、给明确用户提示（如"同步<外部系统>失败，请重新操作"）。

## 4. JSON 处理（沙箱约束）
- 沙箱不便用 `System.Text.Json`（需 ILMerge）。优先：`DataContractJsonSerializer`(定 DTO) 或 ILMerge `Newtonsoft.Json`。
- 原始响应可先回填到出参/字段，再逐步补字段映射。

## 5. 注释与可改性
- 每个插件类头注：对应哪个 Custom API、做什么、依赖哪些环境变量。
- 未完成的映射用 `// TODO:` 标注，便于后期接手补全。
- 端点/选项集实际值未定的，注明"按官方文档/环境核对"。

## 6. 注册（Web API，不依赖 pac）
- pluginassembly(base64) + plugintype + 绑定 Custom API 的 `PluginTypeId`。
- 改代码后 `dotnet build` → PATCH `pluginassembly.content` 热更新。
