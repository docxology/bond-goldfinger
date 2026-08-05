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
| `fig:vault_net` | `output/figures/vault_network.png` |
| `fig:reserve_crisis` | `output/figures/reserve_crisis.png` |
| `fig:laser` | `output/figures/laser_burn_through.png` |
| `fig:laser_engagement` | `output/figures/laser_engagement.png` |

Each row must correspond to a renderer named in
`goldfinger.figures.FIGURE_RENDERERS` and to a `{#fig:...}` anchor in
`03_results.md`. Adding a renderer without adding both leaves an orphan.

## Citations

BibTeX keys in `references.bib` (real BibTeX — it is merged into the
compendium's unified bibliography by `bond-manuscript`), cited as `@key` /
`[@key]`. The human-readable list is `99_references.md`, grouped by attack
surface; the two must agree. Available keys:

`walras1874elements`, `hicks1946value`, `kyle1985continuous`,
`krugman1979model`, `flood1984collapsing`, `garcia2007design`,
`dijkstra1959note`, `israeli2002shortest`, `steen2010laser`,
`carslaw1959conduction`, `siegman1986lasers`, `bondapi2026protocol`.

Every entry must be a source you can actually verify. A fabricated citation is
a worse defect than a missing one — if you are not confident a reference is
real, remove it.
