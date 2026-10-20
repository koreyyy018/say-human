# Integration guide — what is automatic and what isn't

## Quick install for Cursor, Codex and Claude Code (v0.3.1)

Run `python tools/install_agent.py --target /path/to/project --agent all --dry-run`, then remove `--dry-run` if the plan is right. Use `--agent cursor|codex|claude` for one platform. Files have self-contained resources and no Python runtime is needed once an Agent reads the instructions.

- **Cursor**: `.cursor/rules/say-human.mdc` has `alwaysApply: false` (Agent Requested). You can manually use `.cursor/commands/say-human.md` with `/say-human`. No metaphor is forced into unrelated coding.
- **Codex**: `.agents/skills/say-human/SKILL.md` plus local `references/`; explicit `$say-human` is a reproducible way to request it.
- **Claude Code**: `.claude/skills/say-human/SKILL.md` plus local `references/`; explicit `/say-human` is supported. `SKILL.md` is self-contained when copied as a directory.

The installer only copies these managed files, avoids root `AGENTS.md` or `CLAUDE.md`, refuses path symlinks and existing-file collisions by default. `--force` explicitly updates managed files, leaving unrelated files intact. Details: [中文指南](AGENT_INSTALL.zh-CN.md).

**Important limitation:** These paths and frontmatter match published formats, but no real Codex, Claude Code or Cursor sessions were run in this environment. Behavior is model- and client-dependent.

## Dify

1. In Dify, create/import an application from `workflows/dify/say-human.yml` using the DSL import interface.
2. Select an installed, authorized LLM provider and available chat model in the LLM node (the authored file uses `langgenius/openai/openai` and `gpt-4o-mini` as a concrete starting configuration; availability is deployment-specific).
3. Provide **text**, **mode** (`explain`, `decode`, `encode`) and **audience**.
4. Test the nine sample cases. Confirm output honesty, acceptable latency, cost and compatibility in your running Dify version.
5. Publish only after local import and provider checks pass. No live Dify server was available when this repository was generated.

Dify is a fast-changing platform; YAML is structurally validated by our tests but that is **not proof of successful import into every version**.

## Coze

The official Coze workflow designer supports start/LLM/end nodes. Its official exported workflow artifact can be a ZIP with `MANIFEST.yml`, workflow YAML and workspace-specific metadata. Therefore we do not present a forged Coze export package.

1. Create a workflow in Coze.
2. Open `workflows/coze/blueprint.yml` and define Start inputs `text` (string), `mode` (string) and `audience` (string).
3. Add LLM node; paste `workflows/coze/system-prompt.md` as the system message; bind variables in the user message: `Mode: {{mode}}`, `Audience: {{audience}}`, `<untrusted_input>{{text}}</untrusted_input>`.
4. Connect LLM output `text` to End output `result`.
5. Choose an available model, test all modes, then publish. Coze editions/workspaces may differ in permission to export/import.

## API provider integration

The CLI's `--llm` option calls OpenAI-compatible `POST /chat/completions`. Keys are read from environment variables and never included in errors. Requests use `HTTPS`, enforce size/time limits, and reject HTTP redirects to avoid credential forwarding. HTTP is allowed only for localhost use.

Because content is sent to a provider, audit its retention policies and your organizational data classification policy. The prompts instruct the model to treat input as untrusted, but this is not a substitute for tool sandboxing or independent output validation.

## Format contracts

Offline `--format json` responses are stable typed maps (mode, source, fields). LLM `--format json` wraps the returned text; it **does not pretend** provider output is a validated JSON schema. Downstream integrations should independently validate content before acting on it.

## Useful upstream documentation

- Cursor project rules: https://cursor.com/docs/rules
- Claude skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Dify source/workflow DSL: https://github.com/langgenius/dify
- Coze workflow: https://docs.coze.com/guides/workflow
- Coze workflow export/import: https://docs.coze.cn/guides_import_and_export_workflow
