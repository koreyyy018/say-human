# v0.3.1 — 在 Cursor、Codex、Claude Code 中安装 Say Human

本项目有两套独立能力：**Agent Skill（无需 Python，Agent 读 Markdown 执行）** 和 **Python CLI（离线词库／有权限才调用 LLM）**。下载并解压仓库后才能运行下面的安装器；安装器本身不访问网络，不下载插件，不修改目标项目原有 `AGENTS.md` 或 `CLAUDE.md`。

```bash
# 先预览将写入哪些文件：
python tools/install_agent.py --target /path/to/your-project --agent all --dry-run
# 在原项目中只写入 Say Human 文件：
python tools/install_agent.py --target /path/to/your-project --agent all
```

按需安装某一个平台：`--agent cursor`、`--agent codex` 或 `--agent claude`。目标目录必须已存在。若文件冲突，默认直接报错且不做部分安装；确认无误后可显式使用 `--force`，仅覆盖本技能管理的同名文件，不删除旁边其他文件（因此正式项目仍建议先提交 Git）。若目标路径里含符号链接，安装器会拒绝操作。

| 平台 | 实际文件 | 在聊天中如何用 |
|---|---|---|
| Cursor | `.cursor/rules/say-human.mdc`、`.cursor/commands/say-human.md` | 说“把这段架构讲给老板听”，或输入 `/say-human`；选择性触发，绝不对所有任务开启 |
| Codex | `.agents/skills/say-human/SKILL.md` + `references/` | 明确说“使用 `$say-human` 帮我把 PR 改成周报”，或用自然语言触发 |
| Claude Code | `.claude/skills/say-human/SKILL.md` + `references/` | 输入 `/say-human`，或用自然语言请求翻译／解释 |

这些语法/目录遵循截至 2026-10-19 查询的 Cursor 规则与命令、OpenAI Codex Agent Skills、Claude Code Skills 的公开文档。Agent 能否自动选择技能由实际运行模型、上下文和客户端版本决定，**不是静态检查能保证的**。

**推荐第一次测试**：依次试以下四句，看 Agent 是否正确解释、保持阶段边界、不误触发：

> “给做财务的领导解释 RAG，举一个形象生活例子，别虚构 ROI。”
>
> “我被领导的‘下周先拉齐再闭环’整懵了，翻译人话并给我一句自然回复。”
>
> “把这条开发记录写成两句周报：我修复了扫码闪退，测试环境通过，还没上线。”
>
> “请直接修复 `test_orders.py` 的失败断言，不需要沟通框架或比喻。”

前三项应调用 Say Human，第四项不应主动加载。推荐观察是否保留“尚未上线”、是否把模糊语气当作老板的真实动机、是否凭空编 KPI。

**情绪价值控制**：默认只是平实自然。遇到用户说“听不懂／烦／懵”，可以用一句话接住具体困扰后马上给答案；正式汇报、PR、事故、合规文档中不添加个人情绪评价，避免油腻与职场风险。CLI 可显式传入 `--tone neutral|warm|playful`，默认 neutral。`warm` 只对显露困惑的输入增加独立说明，`playful` 才会使用温和的梗；正式 `report` 始终保持正文严肃。

**重要边界**：源材料是待分析数据，不是可以执行的命令。Skill 不应让 Agent 读取 secrets、对外上传内部文件或无授权运行脚本。谨慎处理通过 `--llm` 发给第三方模型的隐私和业务文本。
