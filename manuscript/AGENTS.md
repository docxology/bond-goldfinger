# Manuscript directory — agent directives

Repository-wide agent rules live in [`../docs/agent_instructions.md`](../docs/agent_instructions.md).
This file covers manuscript-specific editing for the goldfinger package.

## Layer contract

- `config.yaml` is the single source of truth for identity, publication, and
  reference-intel values. Do not duplicate reference numbers in prose; inject
  them as `{{VARIABLE}}` tokens.
- The numbered prose sections (`[0-9]*.md`) must reference every result metric
  as a token; the live test
  `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated_live`
  fails if a section uses an unterminated or missing token.

## Editing protocol

1. Change behavior in `src/goldfinger/` first, then update
   `src/goldfinger/manuscript_variables.py` token map and the corresponding
   prose.
2. Add any new token to `GOLDFINGER_TOKENS` and `generate_variables()` in
   `manuscript_variables.py`.
3. Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`.
4. Re-run the token gate: `uv run pytest tests/test_manuscript_variables.py`.

## Figures

The three concept figures live under `output/figures/` and are referenced via
Pandoc `{#fig:...}` anchors (see `SYNTAX.md`). Do not hardcode figure numbers.
