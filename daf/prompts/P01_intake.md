# P01 — 需求采集 prompt

## 任务
把飞书需求文档（或本地 BRD）拆成一条条结构化需求，每条按
`templates/requirement-intake.md` 的 YAML 格式输出，写入 Hub 的 requirements/。

## 步骤
1. 读取需求来源（飞书：用 feishu/parse_feishu_doc.py 拉 raw_content；或本地 MD）
2. 识别独立需求点，每条分配 REQ-NNN
3. 为每条推断 module（对照 .dkf/domains/ 的领域名，对齐 DKF）
4. 抽取/补全 acceptance_criteria；把模糊处列入 open_questions
5. 渲染需求清单菜单，等用户 yes 放行

## 放行后
自动 `git commit -m "feat(P01): 需求采集 [DAF]"`，解锁 P02。
