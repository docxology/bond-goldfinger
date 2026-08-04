# Manuscript Syntax Reference

This file documents rendering syntax. It is a *reference*, not a rendered
section — literal `{{VARIABLE}}` and `{#fig:...}` examples here are
illustrative and are excluded from the live token cross-reference gate (which
scans only the numbered `[0-9]*.md` sections).

## Variables

Result and identity metrics are injected with `{{VARIABLE}}` syntax. The
authoritative set is the return value of
`src/goldfinger/manuscript_variables.py::generate_variables()`; the live test
`tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated_live`
gates that every token used in the numbered sections exists.

Example: `{{MARKET_PRICE_GAIN_PCT}}`, `{{VAULT_SCORE}}`,
`{{LASER_BURN_THROUGH_S}}`.

## Figures

Pandoc-crossref anchors: a figure line ends with `{#fig:label}`, referenced in
prose as `@fig:label` (narrative) or `[@fig:label]` (parenthetical).

| Label | File |
|---|---|
| `fig:corner` | `output/figures/market_corner_trajectory.png` |
| `fig:vault` | `output/figures/vault_layered_score.png` |
| `fig:laser` | `output/figures/laser_burn_through.png` |

## Citations

BibTeX keys in `references.bib`, cited as `@key` / `[@key]`; the reference
list is in `99_references.md`.
