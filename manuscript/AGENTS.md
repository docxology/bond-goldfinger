# Manuscript directory — agent directives

Repository-wide agent rules live in [`../docs/agent_instructions.md`](../docs/agent_instructions.md).
This file covers manuscript-specific editing for the goldfinger package.

## Layer contract

- `config.yaml` is the source of truth for identity and publication metadata
  only. Reference-intel values live in the module `REFERENCE_*` constants; the
  `grand_slam:` block here is an unloaded mirror pinned to them by
  `tests/test_reference_intel.py`. Do not duplicate reference numbers in prose;
  inject them as `{{VARIABLE}}` tokens.
- The **rendered** files — the numbered `[0-9]*.md` sections and `preamble.md`,
  as returned by `manuscript_variables.manuscript_prose_paths()` — must
  reference every result metric as a token; the live test
  `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated_live`
  fails if a rendered file uses an unterminated or missing token. Do not write
  a literal `{{...}}` placeholder into a rendered file; put examples in
  `SYNTAX.md`, which is a guide file.
- Do not write a count of anything outside this package (sibling packages, the
  fleet) into prose: there is no token, no producer, and no gate for it.

## Editing protocol

1. Change behavior in `src/goldfinger/` first, then update
   `src/goldfinger/manuscript_variables.py` token map and the corresponding
   prose.
2. Add any new token to `GOLDFINGER_TOKENS` and `generate_variables()` in
   `manuscript_variables.py`.
3. Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`.
4. Re-run the token gate: `uv run pytest tests/test_manuscript_variables.py`.

## Figures

The concept figures live under `output/figures/` and are referenced via Pandoc
`{#fig:...}` anchors (see `SYNTAX.md`). Do not hardcode figure numbers, and do
not state how many figures there are in prose — the `{{GOLDFINGER_FIGURE_COUNT}}`
token is derived from `goldfinger.figures.FIGURE_RENDERERS`. The renderer list,
the figure files, and `SYNTAX.md`'s label table must stay in step; adding a
renderer means adding its label row and its `{#fig:...}` anchor in
`03_results.md`.

## Counts are derived, never typed

Three structural tokens exist so this manuscript can describe itself without a
hand-counted number that rots: `{{GOLDFINGER_MODULE_COUNT}}` (concept modules
found on disk), `{{GOLDFINGER_FIGURE_COUNT}}` (exported renderers), and
`{{GOLDFINGER_TOKEN_COUNT}}` (length of `GOLDFINGER_TOKENS`). If you catch
yourself typing "the six modules" or "39 tokens" into prose, use the token.

## References

`references.bib` is real BibTeX and is merged into the compendium's unified
bibliography by `bond-manuscript`; `99_references.md` is the human-readable
list, and the two must agree. Every entry must be a source you can actually
verify — a fabricated citation is a worse defect than a missing one.
