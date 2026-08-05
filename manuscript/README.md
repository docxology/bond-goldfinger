# Manuscript: goldfinger (GRAND SLAM)

This directory holds the report manuscripts rendered from the numbered markdown
sections, with `{{VARIABLE}}` token substitution performed by
`scripts/z_generate_manuscript_variables.py`.

## File roles

| File | Role |
|---|---|
| `config.yaml` | Identity + publication metadata (loaded), plus a `grand_slam:` mirror of the module `REFERENCE_*` intel (**not** loaded; pinned by `tests/test_reference_intel.py`) |
| `00_abstract.md` … `07_scope_and_related_work.md` | Numbered prose sections (token + figure sources) — **rendered**, so tokens here are live |
| `99_references.md` | Human-readable reference list, grouped by attack surface |
| `references.bib` | Real BibTeX bibliography, merged into the compendium by `bond-manuscript` |
| `preamble.md` | Header / identity block — **rendered**, so its six identity tokens are live and gated |
| `SYNTAX.md` | Figure, citation, and variable syntax reference (a guide file: never substituted) |

There is deliberately no `config.yaml.example`. One used to sit here advertised
as a "reference copy of the configurable surface"; it was stale (version 0.1.0
against a 0.2.0 package, superseded keyword and intel blocks) and it was not
valid YAML — `yaml.safe_load` raised `ScannerError`, so copying it over
`config.yaml` broke `load_mission_config` immediately. It was deleted rather
than repaired, because a second copy of the config is exactly the duplicated
literal this package forbids. `config.yaml` is committed and is the surface.
`test_every_yaml_file_under_manuscript_parses` stops the class from returning.

## Token protocol

All result metrics must use `{{VARIABLE}}` syntax sourced from
`src/goldfinger/manuscript_variables.py::generate_variables()`. Never
hand-author measured numbers in prose — including counts of modules, figures,
or tokens, which have their own derived tokens
(`{{GOLDFINGER_MODULE_COUNT}}`, `{{GOLDFINGER_FIGURE_COUNT}}`,
`{{GOLDFINGER_TOKEN_COUNT}}`).

The set of *rendered* files is defined once, by
`manuscript_variables.manuscript_prose_paths()`: the numbered sections plus
`preamble.md`. Both gates below read that function, so the two cannot scan
different file sets. (They previously globbed `[0-9]*.md`, which left the
preamble's six live tokens ungated — and hid a literal `{{VARIABLE}}` in it
that would have rendered raw into the report.)

Four tests gate this:

- `test_all_manuscript_tokens_are_generated_live` — every `{{TOKEN}}` used in a
  rendered file exists in the generated map.
- `test_declared_token_tuple_equals_the_generated_key_set` — the declared
  `GOLDFINGER_TOKENS` tuple is exactly the generated key set, so a token added
  to one and not the other fails rather than drifting.
- `test_every_token_is_classified_exactly_once` — every token is identity,
  declared input, or computed result; a new token cannot dodge the scan by
  being forgotten.
- `test_no_computed_result_value_is_hardcoded_in_the_prose` — no *scannable*
  computed result value appears in the prose as a literal, with a positive
  control that pastes each such value in turn and confirms it is flagged.
  **Limit:** bare small integers (counts) and categorical words (`medium`,
  `serious`) are not scanned — see `docs/architecture.md` for why and for the
  enumerated list.

Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`

See also: `../docs/agent_instructions.md` and `../AGENTS.md`.
