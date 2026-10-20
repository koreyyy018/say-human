# Contributor/agent instructions for this repository only

This file guides contributions *to Awesome-Say-Human*. It is **not** intended to be installed in other projects. The user-facing communication skill lives at `skills/say-human/SKILL.md` and has selective activation rules.

Before changing behavior, check and update relevant tests and the installable copies for Codex/Claude. Never fabricate metrics, imply a measured LLM uplift without real model tests, or present prompt-injection advice as a runtime security boundary. Preserve the nine original examples and explicit accuracy corrections. Keep independent tooling opt-in. For coding tasks, implement the requested change directly; **do not automatically add metaphors or executive language**.

Run: `python -m pytest`, `python tools/validate_assets.py`, and `python tools/install_agent.py --target <empty-project> --agent all` as smoke tests.

Say Human v0.6.0: when decoding jargon, prefer one natural human-language interpretation and one actionable reply; never start with a generic uncertainty disclaimer. Do not turn unclear motives into assertions.
