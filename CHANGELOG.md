## v0.6.0 (Public Beta)

- Multi-concept offline comparisons.
- Expanded heuristic claim contradiction coverage, with regression cases.
- Improved Chinese executive update cleanup and semantics for vague report feedback.
- 40-case controlled version-to-version comparison and 180-case legacy replay.

## [0.5.0] — 2026-10-20

- Decode now leads with one actionable sentence, drops the repeated blanket disclaimer, and gives recipient-aware Chinese follow-ups without claiming to know anyone's motives.
- Expanded the original offline jargon phrasebook to **355 entries** across broad workplace and sector contexts; new sector-specific phrases include healthcare, banking, manufacturing, logistics, education, HR, government, security, retail, content, games, energy and real estate. The glossary is editorial reference material, not regulatory guidance.
- Added structured fallbacks for unfamiliar wording, preserving the user's language; distinguished lexical matches, semantic fallback and already-plain-language responses. Avoided false jargon readings in quoted titles, literal uses and straightforward requests.
- Added reproducer and full paired results for the previous 10×20 baseline and a new 10×20 Decode-focused stress test. Results are **offline policy/CLI comparisons**, not a live Cursor/Codex/Claude test.
- Added cross-industry jargon reference to the canonical Skill, synced Codex/Claude packages, updated Cursor rule, and added new regressions.

## [0.4.0] — 2026-10-20

- Added a context-aware, five-mode Agent Skill: **Explain, Decode, Encode, Align, Reply**. Context frame covers audience/relationship, channel, intent, risk and expressed emotion; does not intrude on ordinary coding tasks.
- Added self-contained `contexts.md` with 15 hypothetical sector anchors, audience/channel matrix, and concrete rewrite pairs for realistic workflows.
- Reworked empathy guidelines to respond to a specific obstacle without canned flattery or leaking emotional commentary into formal reports.
- Added real **offline `sayhuman align`** with a conservative metric, baseline and acceptance proposal. Added **LLM-only `sayhuman reply --llm`**, explicitly unavailable offline rather than promising arbitrary natural drafting from templates.
- Routed `--recipient`, `--channel` and `--goal` into opt-in model prompting; refreshed embedded prompts for Reply and Align.
- Published reproducible cross-sector release tests and a maintainer-oriented release checklist; old benchmark claims remain labeled as self-defined offline checks, not model performance.

## [0.3.1] — 2026-10-19

- Fixed natural-language offline glossary queries and Chinese language auto-detection.
- Expanded Chinese workplace jargon: 赋能, 抓手, 颗粒度.
- Hardened audit warnings for unsupported deployment, acceptance, compliance, security review, qualitative effect and scale claims; added false-positive regression cases.
- Removed untrusted prompt-style instruction sentences from the offline executive-ready artifact.
- Added 31 regression tests and a new reproducible 15-industry isolated-install simulation report. All local simulated contracts and executions are **not** live Cursor/Codex/Claude runs.

## [0.3.0] — 2026-10-19

- Added canonical, portable `skills/say-human` with self-contained references; installed adapters for Codex and Claude Code.
- Switched Cursor from always-on to agent-requested rule; added `/say-human` command.
- Added safe offline installer with dry-run, explicit force, conflict preflight and symlink rejection.
- Added conditional emotional acknowledgment in skill instructions and optional CLI `--tone`; avoided emotional filler in formal report output.
- Added two-round cross-industry structural agent loading proxy test (360 baseline / 540 retest), 90-case CLI replay, unit tests and CI validation; transparent about non-live vendor testing.

# Changelog

## v0.2.0 — 2026-10-19

- Added 16 fully localized Chinese technical explanations, bilingual persona-focused guidance and 15 explicitly **hypothetical** industry scenarios.
- Improved common English/Chinese offline executive notes (including KYC validation and in-progress rollout wording); three output styles.
- Added `sayhuman report` for evidence-first structured, stage-aware executive updates, with strict input validation and no synthetic ROI.
- Added `sayhuman audit` as a **heuristic** guard for new numerical claims, staging-as-production and risk/compliance overstatement. False positives and misses remain possible.
- Added optional double-response blinded A/B model experiment and manual scoring harness, with network off by default.
- Rechecked original 210 synthetic scenarios, plus 240 compositional industry-concept cases and 60 additional scenario/audit cases. 510/510 passed **automated rules only**; not independently judged prose quality.
- Real LLM model generation was **not** executed. Dify/Coze integrations remain unverified in their hosted editors.

## v0.1.1 — 2026-10-19

- Built a reproducible 210-case cross-industry synthetic benchmark across 15 industries, with separate full offline outputs, baseline comparison and CLI integration results.
- Expanded corporate phrasebook with Chinese explanations, bilingual aliases, homonym disambiguation and a practical clarification question.
- Added curated audience-specific measurement guidance to 16 technical glossary explanations.
- Improved conservative English/Chinese offline rewriting and flagged unsupported ROI, removed anti-fraud checks and unverifiable compliance claims.
- Added 9 targeted pytest regressions and a 45-case non-independent editorial quality review.
- Honest limits: only deterministic offline and local mocked-provider infrastructure are tested, **no live model or Dify/Coze runs**.

## v0.1.0 — 2026-10-19

- First complete project release: offline CLI, optional OpenAI-compatible provider, nine original few-shot examples (verbatim with factual caveats), 16 technical glossary entries and 12 corporate jargon expressions.
- Portable Cursor and Claude Code configurations, editable standalone system prompts, Dify workflow YAML and Coze workflow blueprint.
- MIT licensing, contribution policy, ethics review, GitHub CI and offline structure/integration tests.
- Known limits: no live Dify/Coze import verification, no remote provider account connected, no claimed GitHub launch/star numbers.
