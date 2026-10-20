# Accuracy and ethical editorial policy

## The bright line

A memorable metaphor may simplify **how a mechanism feels**, but not falsely assert how it works. All nine origin stories are retained *verbatim* for transparency as in-context learning examples; each is accompanied by a factual correction in `data/gold-standard.json`.

## Critical corrections

- **RAG:** retrieving good evidence can reduce unsupported answers; it cannot stop them entirely or validate the content of retrieved documents. A doctor analogy is about consulting records, not making real clinical decisions.
- **Context window:** bound on supplied text/media tokens, not longitudinal memory; utilization doesn't guarantee recall.
- **Tokens:** segmentation varies by tokenizer and medium. They are not simply characters and actual cost can be material, especially at scale.
- **API:** software interface analogous to a physical port only in terms of protocol and integration. Vendors, privacy, security, uptime and costs are meaningful implementation work.
- **Agent and function calling:** models may propose actions but cannot bypass tools, authorization, business rules or human sign-off.
- **Quantization:** lower precision may affect quality, and memory savings need not imply faster inference.
- **Executive language:** no invented 40% uplift, $ saved, deployment success, team impact or numbers sourced only from wishful thinking.
- **Corporate decoding:** “synergy” is an unclear phrase, not proof that a colleague is manipulative. Interpret intent as a hypothesis, not a finding.

## Contributor review checklist

- [ ] A technical definition that withstands expert review.
- [ ] A visual everyday scene (actor, action, consequence), not an abstract synonym.
- [ ] A measured business benefit **or** proposed method to measure it.
- [ ] Specific limit showing where the analogy breaks.
- [ ] No fictional metrics or invented corporate intent.
- [ ] Only share data you're authorized to disclose.

## Security and privacy

Offline glossary/phrasebook/rewrite runs without network. `--llm` submits user text to the configured provider. Avoid putting credentials, personal records, internal strategy, or unredacted customer data into unapproved hosted models. Prompt injection can influence output; treat model responses as untrusted and do not give generated output direct execution privileges.
