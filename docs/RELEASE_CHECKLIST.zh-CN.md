# GitHub 发布检查（v0.6.0）

- 建议版本名 `v0.6.0-beta.1`，保留 Public Beta 定位；不要把本地对照称为模型质量提升。
- 上传解压后的 `Awesome-Say-Human` 根目录，保留 `.agents` / `.claude` / `.cursor` / `.github` 隐藏目录。
- 安装器：`python tools/install_agent.py --target /path/to/your/project --agent all --dry-run`，确认后删掉 `--dry-run`。
- CLI：`python -m pip install -e .`，然后 `sayhuman decode "领导说下周对齐口径、月底闭环"`。
- 三端 Skill 文件由 `python tools/sync_skill.py --check` 核对；源数据和可安装 wheel 内容由 `python tools/sync_assets.py --check` 核对。
- 本地复现 `PYTHONPATH=src python -m pytest -q`；报告见 `docs/V050_DECODE_AB.zh-CN.md`，逐条见 `evals/v050_ab`。
- 发布声明需写明：355 条词库并非逐条外部专家核验；未使用真实 Cursor/Claude/Codex 做开关 A/B；高风险内容需要人工核查。
- 仍需完善：Explain 多概念比较、Encode 部分中文语法、部分行业词条英文描述。
