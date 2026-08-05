# Manuscript: goldfinger (GRAND SLAM)

This directory holds the report manuscripts rendered from the numbered markdown
sections, with `{{VARIABLE}}` token substitution performed by
`scripts/z_generate_manuscript_variables.py`.

## File roles

| File | Role |
|---|---|
| `config.yaml` | Identity + publication metadata + deterministic reference intel |
| `config.yaml.example` | Reference copy of the configurable surface |
| `00_abstract.md` … `07_scope_and_related_work.md` | Numbered prose sections (token + figure sources) |
| `99_references.md` | Human-readable reference list, grouped by attack surface |
| `references.bib` | Real BibTeX bibliography, merged into the compendium by `bond-manuscript` |
| `preamble.md` | Header / identity block |
| `SYNTAX.md` | Figure, citation, and variable syntax reference |

## Token protocol

All result metrics must use `{{VARIABLE}}` syntax sourced from
`src/goldfinger/manuscript_variables.py::generate_variables()`. Never
hand-author measured numbers in prose — including counts of modules, figures,
or tokens, which have their own derived tokens
(`{{GOLDFINGER_MODULE_COUNT}}`, `{{GOLDFINGER_FIGURE_COUNT}}`,
`{{GOLDFINGER_TOKEN_COUNT}}`).

Three tests gate this:

- `test_all_manuscript_tokens_are_generated_live` — every `{{TOKEN}}` used in
  the numbered sections exists in the generated map.
- `test_declared_token_tuple_equals_the_generated_key_set` — the declared
  `GOLDFINGER_TOKENS` tuple is exactly the generated key set, so a token added
  to one and not the other fails rather than drifting.
- `test_no_computed_result_value_is_hardcoded_in_the_prose` — no computed
  result value appears in the prose as a literal (with a positive control
  proving the scan can fail).

Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`

See also: `../docs/agent_instructions.md` and `../AGENTS.md`.
