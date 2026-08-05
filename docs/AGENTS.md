# docs/ — agent directives for the goldfinger documentation set

Scope of this file: how an agent should work on **documentation** inside this
package. For code directives see [`../AGENTS.md`](../AGENTS.md); for the
operational checklist see [`agent_instructions.md`](agent_instructions.md); for
manuscript-specific rules see [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md).

## What lives where

| Document | Owns | Do not put here |
|---|---|---|
| [`README.md`](README.md) | Index of this directory | Substance — link, don't duplicate |
| `AGENTS.md` (this file) | How to work on the docs | Code rules (those are `../AGENTS.md`) |
| [`agent_instructions.md`](agent_instructions.md) | The operational checklist an agent follows | Architecture explanation |
| [`architecture.md`](architecture.md) | Module-by-module structure, the layer contract, the frozen protocol surface | Test strategy |
| [`testing_philosophy.md`](testing_philosophy.md) | No-mock / determinism / gate doctrine, per-file coverage map | Module descriptions |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | **Generated.** Live counts and headline result values | Anything hand-typed |

The package root carries `README.md` (what this package is and how to run it),
`AGENTS.md` (code directives), and `TODO.md` (real remaining work).

## Rules

1. **Never hand-edit `_generated/`.** `docs/_generated/COUNTS.md` is written by
   `scripts/z_generate_counts.py` from
   `goldfinger.manuscript_variables.render_counts_markdown`. Change the renderer
   and regenerate; a test compares the derived lines against a fresh render and
   fails if the committed file is stale.
2. **Do not restate a measured number in prose.** Test counts, coverage
   percentages, module counts, figure counts, and token counts all rot. Cite
   `_generated/COUNTS.md`, use a manuscript `{{TOKEN}}`, or describe the gate
   ("the floor is 90% line+branch") instead of quoting a figure.
3. **Describe modules by name and by what they compute.** A doc that says "the
   domain core" without naming `reserve_attack` and saying it solves for the
   attack time is not documentation. When a module is added or removed, the
   module tables in `architecture.md` and `testing_philosophy.md` are part of
   the change, not a follow-up.
4. **Docs follow code, never lead it.** Change `src/`, run the gate, then write
   what is true. If a doc claims behaviour, open the module and check the claim
   holds today — several of the stale statements cleaned up in this package
   were true when written and false a phase later.
5. **The frozen surface is documented as frozen.** Any description of
   `mission.py` must state which names bond-cli, the coordinator, and the
   orchestrator consume, so a future agent knows what it must not rename.
6. **No exemplar lineage strings.** This package was forked from the template
   exemplar; the placeholder names must not survive. When you need to write the
   lineage grep into a doc, bracket-split the pattern so the doc does not trip
   its own check.

## Before you claim a doc change is done

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/z_generate_counts.py          # if anything structural moved
rg -n "template[_]code_project" .                   # expect zero hits
git status                                          # expect clean after commit
```

Documentation changes that touch `manuscript/` additionally need
`uv run python scripts/z_generate_manuscript_variables.py` and a passing
`tests/test_manuscript_variables.py` token gate.
