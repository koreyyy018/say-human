# Contributing to Say Human

Thank you for making technical communication more understandable without making it less true.

## A useful contribution

Propose a new concept, one grounded scene, a CFO/business translation, and a caveat in `data/concepts.json`. Keep the JSON shape identical to existing entries. Follow `docs/ACCURACY.md`. If your metaphor comes from a real-world source, cite it and ensure you have permission to reuse it.

- Include the exact technical mechanism in one sentence.
- Write a scenario with named objects, actions and consequences.
- Define a metric that *could be measured*; only claim actual effects when verified.
- Mention one failure mode or limit.
- Add an offline CLI test when extending code or built-in transformations.

The original 9 samples in `data/gold-standard.json` are deliberately verbatim; **do not silently rewrite them**. Factual corrections belong in `accuracy_note`. The wheel ships copies in `src/sayhuman/assets/`; run `python tools/sync_assets.py` after changing public assets.

## Run checks

```bash
python -m pip install -e '.[dev]'
python tools/sync_assets.py --check
python tools/validate_assets.py
python -m pytest
```

## Contributor conduct

Critique claims and text, not people. Do not paste private emails, customer data or confidential production logs into public issues. Do not submit fabricated benchmarks, purchased engagement or unverifiable business wins. Maintainers may reject misrepresentative claims even when the prose sounds impressive.
