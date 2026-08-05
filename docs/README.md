# docs — goldfinger (GRAND SLAM)

Agent-facing and maintenance documentation for the **goldfinger** film package
of PROJECT BOND: the GRAND SLAM mission software modelling *Goldfinger* (1964)
as six deterministic concept modules behind a frozen BOND-API mission adapter.

## Contents

| File | Read it when you need… |
|---|---|
| [`AGENTS.md`](AGENTS.md) | The rules for changing documentation in this package — what each doc owns, and why nothing here may restate a measured number |
| [`agent_instructions.md`](agent_instructions.md) | The operational checklist: orientation commands, hard boundaries, where each kind of code goes, the full gate, and this package's known traps |
| [`architecture.md`](architecture.md) | Module-by-module structure of `src/`, how the pieces compose, and exactly how `mission.py` implements (and freezes) the BOND-API `MissionProvider` |
| [`testing_philosophy.md`](testing_philosophy.md) | The no-mock / real-data / determinism doctrine as it applies here, the per-file coverage map, and why gates ship with positive controls |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | Current structural counts and deterministic headline results. **Generated** by `scripts/z_generate_counts.py` — never hand-edited |

## Reading order

New to the package: `agent_instructions.md` → `architecture.md` →
`testing_philosophy.md`. Fixing a specific module: `architecture.md` for what it
computes, then the module's own docstring, which carries the model derivation.

## Elsewhere in the package

- [`../README.md`](../README.md) — what this package is, every module in one
  line, install and run commands, the `MissionProvider` surface
- [`../AGENTS.md`](../AGENTS.md) — code-level agent directives and the layer
  contract
- [`../TODO.md`](../TODO.md) — real remaining work and declared integration
  points
- [`../manuscript/`](../manuscript/) — the numbered report sections,
  `config.yaml` reference intel, and `references.bib`; its
  [`AGENTS.md`](../manuscript/AGENTS.md) covers the token protocol
