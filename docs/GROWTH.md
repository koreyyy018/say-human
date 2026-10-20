# Ethical launch / star-growth playbook

GitHub stars are a lagging proxy for utility; no process guarantees them. Aim for **repeatable demos, portable usefulness and maintained correctness**.

## Why this might spread

- 10-second high-contrast before/after demos: "What's a vector embedding?" / "What did my manager *actually* ask?".
- A shareable `sayhuman decode` result, but never paste confidential company communication without permission.
- A ready-made Cursor rule and Claude Code skill that users can test with no login.
- A clear caveat on every analogy, which makes the repository defensible for working engineers.
- Dual appeal: hard engineering concepts for PM/exec and recognizable workplace jargon for everyday users.

## Week-one release checklist

1. Publish a `v0.1.0` release and tag with this tested ZIP as the source artifact.
2. Record a **genuine** 20–35 second terminal clip: `explain LoRA` → `decode synergy` → `encode bug note`.
3. Create a 6-frame, opt-in post showing technical definition, metaphor, business meaning, caveat, copy-paste update, contributor CTA.
4. Share a *practical walkthrough* in communities where the rules allow it (developer forums, Claude/Cursor circles, relevant subreddits); disclose authorship and avoid repetitive link-dropping.
5. Invite one contribution: a concept with a better analogy and a measurable outcome. Review each submission using docs/ACCURACY.md.
6. Track GitHub traffic and **real** issue/PR participation; do not buy stars, use fake accounts or inflate case studies.

## Growth loops worth building next

- `sayhuman eval`: human-rated correctness, imagery, executive usefulness and honest caveats; compare prompt revisions without made-up scores.
- Optional mini web playground with copy-to-clipboard outputs and privacy controls.
- More language pairs and culture-adapted scenes (`en`, `zh-CN`, `ja`), reviewed by humans.
- Native integrations for Slack/Linear/Jira with explicit user auth, not credential stuffing.
- CI report bot that rewrites PR summaries but only uses observed metrics in the diff/test output.

## Proposed healthy success metrics

Visitors-to-install proxy (releases downloaded / unique traffic if visible), activation (first successful command), continued contribution volume, reported conceptual errors corrected, repeat usage from volunteers, and opt-in newsletter signups. Distinguish raw traffic estimates from measurable active users; don't imply that GitHub stars equal real adoption.
