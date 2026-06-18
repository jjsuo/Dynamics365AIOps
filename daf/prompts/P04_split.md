# P04 — 方案拆解 prompt

## 前置
P03 已出各需求的 FDD + 四象限判定（标准/配置/定制/集成）。

## 任务
把本模块的需求拆成**交付流（stream）**，每个流对应一个解决方案仓，产出
`deliverables/<module>/stream-mapping.json`（格式见 templates/solution-stream-mapping.json）。

## 拆流规则
1. **按象限归流**，四类标准流：
   - `config` — 配置类（实体/表单/BPF/安全角色/经典工作流），无 pro-code
   - `procode` — 插件 / Custom API / PCF / Web 资源等代码
   - `integration` — 接口 / 连接器 / 虚拟表 / 外部系统对接
   - `migration` — 数据迁移
2. 每个流写明 `solution`(解决方案 unique name) + `owner` + 它承载的 `requirements`(REQ-ID 列表)。
3. **空流不建**：没有该象限需求的流，requirements 留空或整条删掉，不造空壳。
4. 一条需求可落到多个流（如既要建实体又要写插件）——在各流的 requirements 里都列上，FDD 里标清依赖。

## 关键约束
- solution 命名遵循项目既定前缀规范，**不在框架里写死客户前缀**（从需求/已有 solution 推断）。
- 标注**跨流依赖**（如 procode 依赖 config 先建好实体）→ 决定 S 阶段的构建顺序，写进各流备注。

## 放行
拆解结果 yes 放行后 commit `feat(P04): 方案拆解 [DAF]`，解锁 P05。
