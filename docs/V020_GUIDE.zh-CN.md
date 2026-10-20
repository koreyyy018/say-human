# v0.2.0 使用指南｜解释行业场景 + 审核工作汇报

该版本包含离线词库与规则工具，无需 API Key。任意复杂自由文本的智能改写需要显式使用 `--llm` 与外部模型；离线规则不是一个泛化的中文文本大模型。

## 快速开始

```bash
python -m pip install -e .
sayhuman industries
sayhuman explain "LoRA" --lang zh --industry ai --audience cfo --format json
sayhuman decode "请大家拉齐口径，下周做好闭环。" --industry government
sayhuman encode "模型接口经常超时，今天加了重试，还没上生产。" --industry ai --style weekly
```

目前支持 `ai, finance, healthcare, manufacturing, ecommerce, education, logistics, hr, government, retail, media, security, gaming, energy, realestate`。所提供的行业应用均明确标为**假设案例**，不能拿来作为真实客户案例。

## 高质量工作汇报：建议使用 report，而不是只传一句口语

在真实周报中，最好提供四类可核实数据：做了什么、处于哪个阶段、证据是什么、什么还没完成。`report` 接收 JSON 文本（也支持 `--stdin`）。

```bash
sayhuman report '{"action":"修复 PDA 扫码重复回调","subject":"仓储派单服务","status":"staging_validated","evidence":["50 条模拟回调通过"],"limitations":["尚未压测","未上线"],"next_step":"完成压测并申请灰度"}' --lang zh --style weekly
```

允许字段：`action`、`subject`、`status` 必填；`evidence`、`limitations` 为非空字符串数组；`outcome`、`next_step` 可选。状态只能是 `investigating`（排查中）、`in_progress`（进行中）、`implemented`（实现完成）、`staging_validated`（测试环境验证）、`deployed`（用户声称已上线）。**实现完成 ≠ 已上线，测试通过 ≠ 取得经济收益**。

`--style` 可选 `executive`、`concise` 或 `weekly`，原始数据不变；程序保留证据来源说明。

## 审计工具 audit

```bash
sayhuman audit 'Fixed a bug; no measurement performed' --candidate 'Increased throughput 40%' --format json
```

会检测候选文本中新增的数字、原文仅测试却声称正式上线、未验证却宣称验证完毕、绝对化承诺等**部分**风险。只做基于模式的启发式判断，不读取后台数据，不核实指标来源，不具备合规审查能力，不能把无风险标记理解成内容真实。

## 何时用 LLM

对不在离线词库的术语、需要真正深入写作的长文本或多轮上下文，可用 `--llm`，但输入会发到配置的 API 提供商。不要未经授权上传公司秘密、患者资料、个人信息或第三方数据。实际模型输出在生产使用前需要人工复核，必要时执行 `audit`。

```bash
export SAYHUMAN_API_KEY='your-secret-key'
export SAYHUMAN_MODEL='your-chat-model'
sayhuman encode 'Raw technical work note' --llm
```

## 本地质量检测

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python tools/sync_assets.py --check
python tools/validate_assets.py
python evals/run_benchmark.py --output evals/rechecked.json
python evals/run_v020.py
python evals/ab_compare.py --max-cases 12 # 只检查，不请求 API
```

评分不能等同内容质量：这些都是合成测试或由参数组合构造的输入。未进行真实模型付费生成，也没有第三方行业专家双盲评估。
