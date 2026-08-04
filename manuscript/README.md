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
| `99_references.md` | Reference list |
| `references.bib` | BibTeX bibliography |
| `preamble.md` | Header / identity block |
| `SYNTAX.md` | Figure, citation, and variable syntax reference |

## Token protocol

All result metrics must use `{{VARIABLE}}` syntax sourced from
`src/goldfinger/manuscript_variables.py::generate_variables()`. Never
hand-author measured numbers in prose. The live test
`tests/test_manuscript_variables.py` asserts every `{{TOKEN}}` in the numbered
sections exists in the generated map.

Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`

See also: `../docs/agent_instructions.md` and `../AGENTS.md`.
