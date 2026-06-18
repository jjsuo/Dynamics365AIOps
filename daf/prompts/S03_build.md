# S03 — 配置 & 编码实现 prompt

## 任务
按 S01 详细设计实现，产物三件套：
1. **配置**：在 dev 环境配实体/表单/BPF/flow/安全角色 → 同步进 unmanaged solution
2. **配置工作簿**：把配置项记成可复核的 workbook（哪个实体加了哪个字段、哪个 flow 干什么）
3. **pro-code**：plugin(C#)/PCF(TS)/JS，写进解决方案仓源码目录

## 源码化
配置完成后用 `pac solution clone/sync` 把 unmanaged solution 拆成源码进 Git
（见 scripts/solution_export.sh 的 sync 段）。每次提交规范 `feat(S03): <module> 配置 [DAF]`。
