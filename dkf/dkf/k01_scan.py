"""K01 元数据扫描：把 Dataverse 的元数据扫成结构化 JSON。

产出（对应 VKF 的 service-meta/，写入 .dkf/meta/）：
  K01_A_entry_points.json     业务入口：插件步骤 / Custom API / flow 触发器
  K01_B_dependencies.json     外部依赖：连接引用 / 自定义连接器
  K01_C_entity_topology.json  实体清单 + 关系拓扑
  K01_E_optionsets.json       全局 OptionSet / 枚举
  K01_G_security.json         安全模型：BU / Team / Role / 字段安全
  K01_P_processes.json        流程：BPF / Power Automate / 经典工作流 / 业务规则
  K01_X_procode.json          pro-code：插件程序集 / Web 资源(JS/PCF)
  K01_S_solutions.json        解决方案清单
  K01_M_navigation.json       导航：模型驱动应用(appmodule) + 站点地图(sitemap)
  K01_R_ribbon.json           命令栏：现代命令(appaction) + 经典 ribbon 命令
  K09_code_logic.json         代码逻辑补充：扫 code/ 源码，插件碰了哪些实体/环境变量（dkf code 命令）
  index/K09_code_flow.md      代码流程图：Mermaid(插件→实体/外部系统) + 文字对照表（dkf code 命令）

设计原则（继承 VKF v1 教训）：只采"地图"，不替元数据做二次表达。
每条记录都带定位信息（logicalname / id / message / stage），让 AI 能回到
真实定义去看，而不是读一份转述。
"""
from __future__ import annotations

import json
from pathlib import Path

from .client import DataverseClient

# Power Automate / 工作流 category 码
WORKFLOW_CATEGORY = {
    0: "经典工作流(classic workflow)",
    1: "对话(dialog)",
    2: "业务规则(business rule)",
    3: "操作(action)",
    4: "业务流程(BPF)",
    5: "Power Automate(modern flow)",
}


def _write(meta_dir: Path, name: str, rows) -> int:
    path = meta_dir / name
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    if isinstance(rows, dict):
        return sum(len(v) for v in rows.values() if isinstance(v, list))
    return len(rows)


def scan_entities(client: DataverseClient, custom_only: bool) -> list:
    """实体清单 + 自定义字段 + 关系拓扑。"""
    select = ("LogicalName,SchemaName,DisplayName,IsCustomEntity,OwnershipType,"
              "PrimaryIdAttribute,PrimaryNameAttribute,Description")
    path = f"EntityDefinitions?$select={select}"
    if custom_only:
        path += "&$filter=IsCustomEntity eq true"
    out = []
    for e in client.get_all(path):
        out.append({
            "logicalname": e["LogicalName"],
            "schemaname": e["SchemaName"],
            "display": (e.get("DisplayName", {}) or {}).get("UserLocalizedLabel", {}) and
                       (e["DisplayName"]["UserLocalizedLabel"] or {}).get("Label"),
            "is_custom": e["IsCustomEntity"],
            "ownership": e.get("OwnershipType"),
            "primary_id": e.get("PrimaryIdAttribute"),
            "primary_name": e.get("PrimaryNameAttribute"),
        })
    return out


def scan_entity_attributes(client: DataverseClient, logicalname: str) -> list:
    """单实体的自定义字段（用于 K04 领域知识，按需调用，避免一次拉全量）。"""
    sel = "LogicalName,SchemaName,AttributeType,IsCustomAttribute,RequiredLevel"
    path = (f"EntityDefinitions(LogicalName='{logicalname}')/Attributes"
            f"?$select={sel}&$filter=IsCustomAttribute eq true")
    return [{
        "logicalname": a["LogicalName"],
        "type": a.get("AttributeType"),
        "required": (a.get("RequiredLevel", {}) or {}).get("Value"),
    } for a in client.get_all(path)]


def scan_relationships(client: DataverseClient, entity_filter=None) -> list:
    """1:N / N:N 关系拓扑。

    注意：Dataverse 的 RelationshipDefinitions 是抽象基类型，
    ReferencingEntity/ReferencedEntity 等字段只存在于派生类型上，
    直接在基集合上 $select 这些字段会 400，必须按类型 cast 查询。

    entity_filter：若给定一组实体 logicalname，只保留两端至少有一个落在其中的
    关系（配合 custom_only 控量——全量关系动辄数万条，绝大多数是标准关系）。
    """
    out = []
    o2m = ("RelationshipDefinitions/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata"
           "?$select=SchemaName,ReferencingEntity,ReferencedEntity,IsCustomRelationship")
    for r in client.get_all(o2m):
        out.append({
            "schema": r.get("SchemaName"),
            "referencing": r.get("ReferencingEntity"),   # N 端
            "referenced": r.get("ReferencedEntity"),      # 1 端
            "type": "OneToMany",
            "is_custom": r.get("IsCustomRelationship"),
        })
    m2m = ("RelationshipDefinitions/Microsoft.Dynamics.CRM.ManyToManyRelationshipMetadata"
           "?$select=SchemaName,Entity1LogicalName,Entity2LogicalName,IsCustomRelationship")
    for r in client.get_all(m2m):
        out.append({
            "schema": r.get("SchemaName"),
            "referencing": r.get("Entity1LogicalName"),
            "referenced": r.get("Entity2LogicalName"),
            "type": "ManyToMany",
            "is_custom": r.get("IsCustomRelationship"),
        })
    if entity_filter is not None:
        ef = set(entity_filter)
        out = [r for r in out if r["referencing"] in ef or r["referenced"] in ef]
    return out


def scan_optionsets(client: DataverseClient) -> list:
    out = []
    for o in client.get_all("GlobalOptionSetDefinitions?$select=Name,IsCustomOptionSet"):
        out.append({"name": o.get("Name"), "is_custom": o.get("IsCustomOptionSet")})
    return out


def scan_security(client: DataverseClient) -> dict:
    bus = [{"name": b["name"], "id": b["businessunitid"]}
           for b in client.get_all("businessunits?$select=name")]
    roles = [{"name": r["name"], "id": r["roleid"], "bu": r.get("_businessunitid_value")}
             for r in client.get_all("roles?$select=name,_businessunitid_value")]
    teams = [{"name": t["name"], "type": t.get("teamtype")}
             for t in client.get_all("teams?$select=name,teamtype")]
    fsp = [{"name": f["name"]} for f in client.get_all("fieldsecurityprofiles?$select=name")]
    return {"business_units": bus, "roles": roles, "teams": teams, "field_security_profiles": fsp}


def scan_processes(client: DataverseClient) -> list:
    sel = "name,category,primaryentity,statecode,type,_ownerid_value"
    # type eq 1 => 流程定义（排除运行实例）
    path = f"workflows?$select={sel}&$filter=type eq 1"
    out = []
    for w in client.get_all(path):
        cat = w.get("category")
        out.append({
            "name": w.get("name"),
            "category": WORKFLOW_CATEGORY.get(cat, f"未知({cat})"),
            "entity": w.get("primaryentity"),
            "state": "激活" if w.get("statecode") == 1 else "草稿",
        })
    return out


def scan_entry_points(client: DataverseClient) -> dict:
    """业务入口：插件步骤(注册在哪个 message+entity+stage) + Custom API。

    只采"有意义的业务插件"，两道过滤把平台噪声去掉：
      1) 服务端 ishidden eq false —— 排除平台内部步骤(占 ~90%+，在每个实体上
         注册 Create/Retrieve/Assign/Archive... 的 Microsoft.Crm.ObjectModel 等)。
      2) 本地排除 assemblyname 以 'Microsoft.' 开头的第一方程序集，只留客户/ISV
         自己的业务插件(即非 Microsoft.* 的程序集)。
    保留 assembly 字段做定位，便于回到真实插件定义。
    """
    step_path = ("sdkmessageprocessingsteps?$filter=ishidden/Value eq false"
                 "&$select=name,stage,mode,rank,statecode"
                 "&$expand=sdkmessageid($select=name),"
                 "sdkmessagefilterid($select=primaryobjecttypecode),"
                 "plugintypeid($select=assemblyname)")
    stage_map = {10: "PreValidation", 20: "PreOperation", 40: "PostOperation"}
    steps = []
    for s in client.get_all(step_path):
        assembly = (s.get("plugintypeid") or {}).get("assemblyname") or ""
        if assembly.startswith("Microsoft."):   # 跳过微软第一方/平台程序集
            continue
        msg = (s.get("sdkmessageid") or {}).get("name")
        ent = (s.get("sdkmessagefilterid") or {}).get("primaryobjecttypecode")
        steps.append({
            "name": s.get("name"),
            "message": msg,            # Create / Update / Delete ...
            "entity": ent,
            "stage": stage_map.get(s.get("stage"), s.get("stage")),
            "mode": "异步" if s.get("mode") == 1 else "同步",
            "assembly": assembly,
            "state": "激活" if s.get("statecode") == 0 else "禁用",
        })
    custom_apis = []
    capi_path = ("customapis?$select=uniquename,name,bindingtype,boundentitylogicalname,"
                 "isfunction,allowedcustomprocessingsteptype")
    for c in client.get_all(capi_path):
        custom_apis.append({
            "uniquename": c.get("uniquename"),
            "name": c.get("name"),
            "bound_entity": c.get("boundentitylogicalname"),
            "is_function": c.get("isfunction"),
        })
    return {"plugin_steps": steps, "custom_apis": custom_apis}


def scan_dependencies(client: DataverseClient) -> dict:
    """外部依赖：连接引用 / 自定义连接器。"""
    conn_refs = [{"name": c.get("connectionreferencedisplayname"),
                  "logicalname": c.get("connectionreferencelogicalname"),
                  "connector": c.get("connectorid")}
                 for c in client.get_all(
                     "connectionreferences?$select=connectionreferencedisplayname,"
                     "connectionreferencelogicalname,connectorid")]
    return {"connection_references": conn_refs}


def scan_procode(client: DataverseClient) -> dict:
    assemblies = [{"name": a.get("name"), "version": a.get("version"),
                   "isolation": a.get("isolationmode")}
                  for a in client.get_all("pluginassemblies?$select=name,version,isolationmode")]
    # webresourcetype: 1=HTML 3=JScript 8=Resx ... PCF 控件在 customcontrols
    # 服务端就只取 JS(=3)，避免把整库 Web 资源(可达数万条)全拉回本地再过滤。
    web_resources = [{"name": w.get("name"), "type": w.get("webresourcetype")}
                     for w in client.get_all(
                         "webresourceset?$select=name,webresourcetype&$filter=webresourcetype eq 3")]
    pcf = [{"name": c.get("name")} for c in client.get_all("customcontrols?$select=name")]
    return {"plugin_assemblies": assemblies, "js_web_resources": web_resources, "pcf_controls": pcf}


def scan_navigation(client: DataverseClient) -> dict:
    """K01_M 导航：模型驱动应用(appmodule) + 站点地图(sitemap)。
    给 AI 补"系统从哪进、有哪些应用/区域"，元数据扫描原本缺这块。"""
    out = {"apps": [], "sitemaps": []}
    try:
        out["apps"] = [{"name": a.get("name"), "uniquename": a.get("uniquename")}
                       for a in client.get_all("appmodules?$select=name,uniquename")]
    except Exception as ex:  # 权限/版本差异不致命
        out["apps_error"] = str(ex)
    try:
        out["sitemaps"] = [{"unique": s.get("sitemapnameunique")}
                           for s in client.get_all("sitemaps?$select=sitemapnameunique")]
    except Exception as ex:
        out["sitemaps_error"] = str(ex)
    return out


def scan_ribbon(client: DataverseClient) -> dict:
    """K01_R 命令栏/自定义按钮：现代命令(appaction) + 经典 ribbon 命令(ribboncommand)。
    元数据扫描原本不含按钮，这里补上"界面上有哪些自定义动作入口"。"""
    out = {"app_actions": [], "ribbon_commands": 0}
    try:
        out["app_actions"] = [{"name": a.get("name")} for a in client.get_all("appactions?$select=name")]
    except Exception as ex:
        out["app_actions_error"] = str(ex)
    try:
        # ribboncommand 量可能较大，只计数 + 取少量样例做定位
        rows = list(client.get_all("ribboncommands?$select=command,_ribboncustomizationid_value"))
        out["ribbon_commands"] = len(rows)
        out["ribbon_commands_sample"] = [r.get("command") for r in rows[:20]]
    except Exception as ex:
        out["ribbon_commands_error"] = str(ex)
    return out


def scan_solutions(client: DataverseClient) -> list:
    sel = "uniquename,friendlyname,version,ismanaged"
    path = f"solutions?$select={sel}&$filter=isvisible eq true"
    return [{
        "uniquename": s.get("uniquename"),
        "friendly": s.get("friendlyname"),
        "version": s.get("version"),
        "managed": s.get("ismanaged"),
    } for s in client.get_all(path)]


def scan_code_logic(code_dir: Path) -> dict:
    """K09 代码逻辑补充：扫本地 code/ 下的插件源码(.cs)，抽出"这段代码碰了哪些实体/
    环境变量/是不是插件"，把 API 元数据看不到的业务逻辑补回知识库。
    无代码目录则给出"建议补充代码"的提示，供 K04 标注。"""
    import re
    result = {"code_dir": str(code_dir), "files": [], "note": None}
    if not code_dir.exists():
        result["note"] = f"未找到代码目录 {code_dir}：相关 Custom API/插件逻辑无源码，建议补充代码后重扫。"
        return result
    cs_files = list(code_dir.rglob("*.cs"))
    if not cs_files:
        result["note"] = "代码目录存在但无 .cs 文件：若有 Custom API/插件未实现，建议补充代码。"
    re_cls = re.compile(r"class\s+(\w+)\s*:\s*([\w\.<>,\s]+)")
    re_ent = re.compile(r'(?:new\s+Entity|Retrieve(?:Multiple)?|QueryExpression)\s*\(\s*"([a-z0-9_]+)"')
    re_env = re.compile(r'GetEnvVar\([^,]+,\s*"([a-zA-Z0-9_]+)"')
    for f in cs_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        classes = [{"name": m.group(1), "is_plugin": "IPlugin" in m.group(2)} for m in re_cls.finditer(txt)]
        entities = sorted(set(re_ent.findall(txt)))
        env_vars = sorted(set(re_env.findall(txt)))
        if classes or entities or env_vars:
            result["files"].append({
                "file": str(f.relative_to(code_dir)),
                "classes": classes,
                "entities_touched": entities,
                "env_vars": env_vars,
            })
    return result


def build_code_flow_md(result: dict) -> str:
    """把 scan_code_logic 的结果渲染成 Mermaid 流程图(markdown)。
    每个插件类 → 它碰的实体(读写) + 用的环境变量(外部系统凭据/端点)。
    让"代码做了什么流程"可视化，补 API 元数据看不到的运行逻辑。"""
    def ext_of(env: str) -> str:
        """从环境变量名**结构化推导**外部系统名（不写死任何项目词，保持框架标准化）：
        去掉发布者前缀(prefix_) 与常见凭据/端点后缀，剩下的词即系统名。
        例：<pfx>_FooApiToken -> Foo；<pfx>_BarBaseUrl -> Bar；无法推导则 '外部系统'。"""
        s = env.split("_", 1)[1] if "_" in env else env  # 去发布者前缀
        for suf in ("ApiBaseUrl", "ApiBaseURL", "BaseUrl", "BaseURL", "ApiToken",
                    "ApiKey", "ApiSecret", "ApiUser", "Endpoint", "Token", "Secret",
                    "User", "Password", "Key", "Url", "URL", "Api"):
            if s.endswith(suf):
                s = s[: -len(suf)]
                break
        return s or "外部系统"
    lines = ["# 代码流程图（dkf code 自动生成，源自 code/ 源码）", "",
             "> 节点：▭ 实体 · (( )) 外部系统 · 插件类。边：实体=读写，外部=调用。", "",
             "```mermaid", "flowchart LR"]
    seen_ext = {}
    for f in result.get("files", []):
        plugins = [c["name"] for c in f.get("classes", []) if c.get("is_plugin")]
        for p in plugins:
            lines.append(f"  {p}([{p}]):::plugin")
            for ent in f.get("entities_touched", []):
                lines.append(f"  {p} -->|读写| ENT_{ent}[{ent}]")
            for env in f.get("env_vars", []):
                ext = ext_of(env)
                node = f"EXT_{ext}"
                seen_ext[node] = ext
                lines.append(f"  {p} -.->|{env}| {node}(({ext}))")
    lines += ["  classDef plugin fill:#def,stroke:#36c;", "```", ""]
    # 文字版对照表（便于无 Mermaid 渲染时也可读）
    lines.append("## 对照表")
    lines.append("| 插件 | 碰的实体 | 调用外部(经环境变量) |")
    lines.append("|---|---|---|")
    for f in result.get("files", []):
        for c in f.get("classes", []):
            if not c.get("is_plugin"):
                continue
            ents = ", ".join(f.get("entities_touched", [])) or "-"
            envs = ", ".join(f.get("env_vars", [])) or "-"
            lines.append(f"| {c['name']} | {ents} | {envs} |")
    return "\n".join(lines) + "\n"


def run_k01(client: DataverseClient, out_dir: Path, custom_only: bool = True) -> dict:
    meta = out_dir / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    summary = {}

    entities = scan_entities(client, custom_only)
    # custom_only 时只取与已扫实体相关的关系；全量扫描(custom_only=False)则不过滤
    ent_filter = {e["logicalname"] for e in entities} if custom_only else None
    rels = scan_relationships(client, entity_filter=ent_filter)
    summary["K01_C_entity_topology.json"] = _write(
        meta, "K01_C_entity_topology.json", {"entities": entities, "relationships": rels})

    summary["K01_E_optionsets.json"] = _write(meta, "K01_E_optionsets.json", scan_optionsets(client))
    summary["K01_G_security.json"] = _write(meta, "K01_G_security.json", scan_security(client))
    summary["K01_P_processes.json"] = _write(meta, "K01_P_processes.json", scan_processes(client))
    summary["K01_A_entry_points.json"] = _write(meta, "K01_A_entry_points.json", scan_entry_points(client))
    summary["K01_B_dependencies.json"] = _write(meta, "K01_B_dependencies.json", scan_dependencies(client))
    summary["K01_X_procode.json"] = _write(meta, "K01_X_procode.json", scan_procode(client))
    summary["K01_S_solutions.json"] = _write(meta, "K01_S_solutions.json", scan_solutions(client))
    summary["K01_M_navigation.json"] = _write(meta, "K01_M_navigation.json", scan_navigation(client))
    summary["K01_R_ribbon.json"] = _write(meta, "K01_R_ribbon.json", scan_ribbon(client))
    return summary
