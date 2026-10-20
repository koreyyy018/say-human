> **v0.6.0｜中文职场黑话表达升级**：默认一句人话直说重点，不再反复输出“以下只是可能的解读”；支持 355 条跨行业术语（含历史和新增词），陌生表达按中文任务线索作保守解释；已明确的要求不强行问 KPI。新增 [两组 200 条的离线 A/B 测试](docs/V050_DECODE_AB.zh-CN.md)，详述新版提升与测试边界。**不是 Cursor/Claude/Codex 的真实大模型效果评分。**

> **v0.4.0｜GitHub Public Beta 发布候选版**：新增五大沟通模式 Explain / Decode / Encode / Align / Reply，按沟通对象、渠道、目标、风险与情绪适配；新增可离线执行的 `align` 和需要显式 `--llm` 的 `reply`。200 条新合成样本的本地规则检查全部通过，**不等于真实 Cursor/Codex/Claude 模型的使用成功率**。查看 [本轮审查](docs/V040_RELEASE_EVAL.zh-CN.md) 与 [上传清单](docs/RELEASE_CHECKLIST.zh-CN.md)。

> 无需调用外部服务也能使用基础 Skill；安装器不会修改你项目的根目录 `AGENTS.md`。直接安装：`python tools/install_agent.py --target /你的项目路径 --agent all`。详见 [安装指南](docs/AGENT_INSTALL.zh-CN.md)。

# 🗣️ Awesome Say Human｜把技术黑话翻译成人话

**AI 工程师说 Token，老板听到的是账单。我们要解决的是两者之间的信息差。**

这不是一个通用提示词合集，而是一个可运行、可嵌入 Cursor / Claude Code / Dify / Coze 的**跨行业沟通翻译层**。同时做两件事：

1. **技术 ↔ 商业价值**：把 RAG、LoRA、Embedding、Agent 工作流等技术说清楚，再给出可验证的 ROI 衡量方法，而不是瞎编节省了多少钱。
2. **职场黑话 ↔ 人话**：把“协同赋能、低垂果实、后续对齐”还原成明确行动；把“修了个破 Bug”改写成专业的工作总结，但不虚构 +40% 性能。

## 🚀 历史能力（自 v0.2.0 起）：行业化解释与事实汇报

现在不只识别职场黑话，还可以输出 16 个概念的完整中文解释、15 个行业的**假设**业务应用，以及可复现的证据审计。行业案例属于帮助理解的设计示意，不代表任何组织真实部署。

```bash
pip install -e .
# 中文技术比喻 + 医院业务示意 + CFO 决策指标
sayhuman explain RAG --lang zh --industry healthcare --audience cfo
# 针对金融行业的英文工作汇报改写
sayhuman encode "Cleaned up the KYC form validation; fewer weird errors but I did not measure the rate." --industry finance
# 两段内容事实差异检查：发现原文不存在的 40% （仅启发式）
sayhuman audit "We fixed a bug" --candidate "We improved throughput 40%"
# v0.4：把模糊目标拆成待确认的验收指标（离线）
sayhuman align "优化医院预约系统响应时间" --industry healthcare --lang zh
# 结构化工作汇报：输入 JSON，明确测试/上线阶段
sayhuman report '{"action":"修复重复工单","subject":"物业工单","status":"staging_validated","evidence":["30 条测试通过"],"limitations":["尚未上线"],"next_step":"安排现场验收"}' --lang zh
# 盲测预检查：不发送网络请求
python evals/ab_compare.py --max-cases 12
```

**重点变化：**`report` 必须明确 `investigating / in_progress / implemented / staging_validated / deployed` 中的状态；只把提供的数据标为“用户陈述”，不替用户确认 ROI。`audit` 是规则检测而非合规证明，能发现一些编造数字和阶段夸大的问题，但可能漏检其他改写。完整参数、盲评流程和使用边界参见 [v0.2 使用指南](docs/V020_GUIDE.zh-CN.md) 与 [A/B 评测协议](docs/EVALUATION_PROTOCOL.md)。

**新的回归结果：510/510 条通过自动规则（210 旧例、240 组合检查、60 新场景）；测试均为合成或组合样本，不代表真实职场用户满意度，也未运行真实模型 A/B。**

## 🔬 210 条跨行业实测（v0.1.1）

针对 15 个行业手工构建 210 条**合成**真实工作场景：60 条技术解释、75 条黑话解码、75 条汇报重写。按仓库预设的自动规则，修复前 52/210，修复后 210/210；**这不是人类用户满意度或真实模型生成质量分数**。另抽查 45 条进行编辑型审阅，10 条基本可直接用、33 条可做初稿、2 条仍需修改。

查看 [完整测试报告](TEST_REPORT.zh-CN.md)、[逐条输入](evals/scenarios.jsonl)、[完整测试输出](evals/final_offline.json) 和 [编辑审阅](evals/QUALITATIVE_REVIEW.zh-CN.md)。测试未调用真实模型 API，也未验证线上 Dify/Coze 导入。自 v0.2.0 起，16 个核心技术概念也提供中文解释；离线模式仍不能理解所有开放领域的任意提问。

## v0.4 新功能：不止技术比喻，还有“可直接发出去”的沟通

Agent Skill 现有五种模式：解释概念、拆解黑话、真实成果包装、模糊需求对齐、针对领导/客户/同事等关系写自然回复。目标不是所有任务都插入比喻，而是**在需要沟通翻译的场合才触发**。遇到用户的困惑或烦躁，先抓具体卡点给予一句自然回应，不把安慰话术塞进给老板看的正式邮件。

CLI 增加 `sayhuman align`；`sayhuman reply` 需要 `--llm` 和显式配置的模型接口，纯离线模式不会假装能处理任意真实聊天。对外发布前须明确：200/200 是本项目编写的离线规则检查，而非实际模型对照提升率。

## 三行试用

```bash
python -m pip install -e .
sayhuman explain "Vector Embeddings" --audience cfo
sayhuman decode "Let's leverage synergy and circle back."
sayhuman encode "Fixed a bug because the previous dev was stupid, now it runs faster."
```

无需 API Key 的离线版本含 16 个技术概念、职场黑话短语表。生成式模式请显式加 `--llm`，并配置 `SAYHUMAN_API_KEY`、`SAYHUMAN_MODEL`；这会把输入发送至对应模型服务。

| 专业名词 | 人话 | 老板最关心的事 |
| --- | --- | --- |
| Vector Embeddings | 超市把“跑鞋”和“运动鞋”放在相邻货架，即使文字不完全相同。 | 检索正确率、用户搜索时间与维护成本。 |
| Fine-tuning | 训练厨师掌握本店秘制菜，而不是每次顾客都重讲菜谱。 | 数据标注、训练成本、质量一致性。 |
| Agentic Workflow | 餐厅前台、配菜、厨师和验收员接力做完一张订单。 | 完成率、人工接管次数、总成本。 |
| LoRA | 在现成西装上改几片布，而不是重新纺一整件衣服。 | 显存和训练开销下降的可能性及质量代价。 |
| Quantization | 把大地图压成口袋版，携带方便但可能丢失细节。 | 部署成本、模型质量、真实硬件加速效果。 |

## 直接集成

- Cursor：`.cursor/rules/say-human.mdc`（根目录 `.cursorrules` 是旧版兼容）
- Claude Code：`.claude/skills/say-human/SKILL.md`，在项目里可以调用 `/say-human`
- Dify：`workflows/dify/say-human.yml`（导入后需要绑定自己的模型并验证）
- Coze：`workflows/coze/blueprint.yml` + `system-prompt.md`（需要在可视化编辑器配置，不宣称是可直接导入的官方导出包）
- 基础风格：`prompts/jargon-aligner.md`
- 两种职场模式：`prompts/corporate-jargon-optimizer.md`

用户提供的 9 条示范都**原样**放入 `data/gold-standard.json`，并成为生成模式的 Few-Shot 参考。另设事实校验备注：例如 RAG 不会彻底消除幻觉、Token 不等于字符、Context Window 不等于永久记忆。

更多安装、测试和贡献方式请参阅 [完整英文 README](README.md)、[集成指南](docs/INTEGRATIONS.md) 以及 [增长计划](docs/GROWTH.md)。
