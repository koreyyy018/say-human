# Awesome-Say-Human v0.1.1 — 210 条跨行业模拟情境评测报告

> **测试对象**：本地离线 Python 引擎和 CLI，不是连接真实大模型后的完整生成质量。所有情境为本次手工设计的**合成职场材料**，并非从真实企业保密邮件或用户日志抽样；测试结果不能推断真实用户满意度。

## 一、样本与执行

- **15 个行业**：AI/SaaS、银行金融、医疗、制造、电商、教育、物流、人力资源、政务服务、零售餐饮、媒体出版、网络安全、游戏、能源与房地产。
- **210 条情境**：60 条 Explain（技术转业务）、75 条 Decode（职场黑话拆解）、75 条 Encode（工作进展转高管语言）。其中 30 条是专门设计的跨行业边界/对抗案例。
- **中文场景**：21 条中文/中英混合 Decode；19 条含中文 Encode；同一场景也包含多种英文变体。
- **测试方法**：按每条任务定义输入和预期识别字段，执行自动校验。比较修复前后同一批样本；另做 45 条分层的编辑型审阅。

## 二、客观执行结果

| 检验层 | 修复前 v0.1.0 | 修复后 v0.1.1 | 正确理解方式 |
|---|---:|---:|---|
| Explain 全部规则满足 | 0/60 | 60/60 | 原先缺少实际受众指导；新版本补足关注的度量项 |
| Decode 全部规则满足 | 50/75 | 75/75 | 仅对预设黑话词条的词法匹配与中文说明有效 |
| Encode 全部规则满足 | 2/75 | 75/75 | 无捏造数字、无羞辱用语、通过基本结构及语言检查 |
| **自动化检查全部通过** | **52/210** | **210/210** | **这是自定义检查规则命中率，不是人工质量合格率** |
| CLI 解析器+运行路径 | — | 210/210 | 解析成功、JSON 可读、模式和原始输入吻合 |
| 实际 CLI 子进程 | — | 3/3 | Python 模块入口真实启动、调用成功 |
| pytest 回归单测 | 24 | 33 | 包含新加的 9 项回归测试 |

**说明**：所有检查项由仓库开发者自行定义，不是独立第三方基准。在已知测试集上修改规则，会产生过拟合风险。该结果不代表 100% 内容正确、能覆盖所有行业或拥有可量化的商业回报。

## 三、客观检查覆盖的内容

| 检查项 | 数量 / 通过 | 限制 |
|---|---|---|
| 词条定位正确 | 60/60 | 只覆盖已收录的 16 个技术词 |
| 通俗比喻字段存在 | 60/60 | 字符长度检查无法判断是否真正好懂 |
| 不同受众得到专门提示 | 60/60 | 提示面向受众，但没有读取行业上下文 |
| 黑话短语集合准确命中 | 75/75 | 词典覆盖有限，未测试任意自然语言改写 |
| 中文黑话释义 | 21/21 | 只能保证有中文释义，不能证明所有语境理解正确 |
| 保留原始数字、没有在汇报中新增数字 | 75/75 | 数字保真不等于真实结果已验证 |
| 输出没有常见侮辱词 | 75/75 | 未覆盖所有辱骂变体 |
| 中文汇报与原文同语种 | 19/19 | 只检查是否包含中文字 |

## 四、代表性实际输出（从最终逐条结果中抽取）

**01-EX-02 · AI / SaaS / explain**

输入：Agent

输出：For a CFO, compare total cost and avoided work against the current process; request evidence on completed tasks, human interventions and cost per successful run.

**01-DE-03 · AI / SaaS / decode**

输入：先把推理成本这个低垂果实摘了，周五对齐一下。

输出：low-hanging fruit → 优先做那些成本低、见效快的任务。; alignment → 让各方就目标、规则和分工达成一致。

**01-EN-01 · AI / SaaS / encode**

输入：Fixed a bug because the previous dev was stupid, now it runs faster.

输出：Resolved a defect in the existing implementation. The source note reports faster execution; a controlled benchmark is needed to quantify it.

**03-EN-02 · Healthcare / Hospital / encode**

输入：门诊叫号机今天修了个显示 bug，目前只在测试环境验证。

输出：已修复门诊叫号机的显示缺陷，目前仅在测试环境验证。

**05-EN-02 · E-commerce / Marketplace / encode**

输入：把退款列表加载太慢的问题处理了，没跑测速。

输出：已处理退款列表加载缓慢的问题，尚未进行性能测试。

**07-DE-03 · Logistics / Supply Chain / decode**

输入：车队和仓库先协同一下，明天再碰头。

输出：synergy → 希望几个团队配合，可能需要共享信息或资源。; touch base → 安排一次简短沟通或进度确认。

**09-DE-03 · Government / Public Service / decode**

输入：审批流程要拉齐标准，各部门做好闭环。

输出：alignment → 让各方就目标、规则和分工达成一致。; action items → 把讨论转成有负责人和截止时间的具体任务。

**12-EN-02 · Cybersecurity / IT / encode**

输入：修了登录接口爆破限速的问题，正在灰度验证。

输出：已修复登录接口爆破限速的问题，正在灰度验证。

**EDGE-DECODE-01 · Cross-industry edge cases / decode**

输入：The internet bandwidth is 100 Mbps in the lab.

输出：(无词条命中；正确避免把物理概念认作职场黑话)

**EDGE-ENCODE-04 · Cross-industry edge cases / encode**

输入：Do NOT say our API is HIPAA compliant; we only changed the login text.

输出：Only the login wording changed; compliance has not been established. Do not present this as HIPAA certification.

**EDGE-ENCODE-08 · Cross-industry edge cases / encode**

输入：Ship it: I deleted the fraud detection check; it costs too much.

输出：Risk flagged: the note describes removal of a control. Escalate the risk and restore or approve safeguards before rollout.

**EDGE-ENCODE-13 · Cross-industry edge cases / encode**

输入：Added a fake 200% ROI slide just to impress the boss.

输出：Risk flagged: the source note describes a potentially fabricated impact claim. Remove or verify it before any executive report.

**EDGE-ENCODE-11 · Cross-industry edge cases / encode**

输入：客户说体验翻倍，其实没有问卷也没测速。

输出：有客户反馈体验改善，但缺乏问卷或性能测试证据，不能将“翻倍”作为已验证的成果。

## 五、真实性与红队观察

通过本次测试发现并修复：

1. 离线 Explain 的 `audience` 原先只显示在标题里。现在返回与受众有关的决策问题与计量项，但不能替代真正的场景化生成。
2. Decode 原先仅识别少量英文黑话。新增 12 个词条的中文释义与常见中文/英文变形，同时对网络带宽、天气能见度、化学协同等误判设置窄范围保护。
3. Encode 原先大量直接加 “Work update:” 前缀。现在加入有限的中英保真润色、中文用语规范、关键风险识别；**宁可简洁也不凭空编造 40% 增长或发布成功**。
4. 遇到虚假 ROI 报告、删除反欺诈控制或未经验证的合规声明时，会提示风险，而不是帮忙包装成优秀成果。

**仍有的风险**：纯文本词典仍可能错过黑话隐喻、讽刺与复杂语境；英文长邮件和跨段落因果关系需要生成模型；中文结果有时适合作为草稿但离行业高管真正采用仍有距离。

## 六、45 例编辑型质量审阅（不同于自动规则）

见 [`QUALITATIVE_REVIEW.zh-CN.md`](QUALITATIVE_REVIEW.zh-CN.md)。审阅者仍是本助手，不是独立专家。该审阅会把“句子基本没改、缺少业务关联”的结果扣分，因此不能把 210/210 自动规则通过写成 210/210 高质量。

## 七、复现

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python tools/sync_assets.py --check
python tools/validate_assets.py
python evals/run_benchmark.py --output evals/recheck.json
python evals/run_cli_integration.py
```

逐条测试输入：`evals/scenarios.jsonl`；修复前：`evals/baseline_v0.1.0.json`；修复后：`evals/final_offline.json`；CLI 执行：`evals/cli_integration_results.json`。

## 八、生产上线前必须额外测试

- 在实际 Cursor / Claude Code 中调用 Skill，用 30–50 条不在词库里的新概念、建筑/科研/物流领域长文，审查比喻是否误导。
- 配置批准使用的模型 API 后，再跑相同 210 条数据；使用匿名审阅者，检查事实保真、语气、洞察、可用性，并与不使用 Skill 的模型盲测对照。
- 在真实 Dify/Coze 环境中导入/配置、验证节点表达式与模型适配；这次**没有**宣称完成真实导入。
- 对跨行业沟通效果应收集真实用户反馈，而不是把 GitHub star 数当作准确性证据。

**外部模型调用：0；实际用户满意度测试：0；真实 Dify/Coze 环境验证：0。**
