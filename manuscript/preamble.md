# Preamble

This manuscript is rendered from the numbered markdown sections in this
directory, with `{{VARIABLE}}` token substitution performed by
`scripts/z_generate_manuscript_variables.py` from
`src/goldfinger/manuscript_variables.py::generate_variables()`.

Identity: **{{GOLDFINGER_TITLE}}** · film **{{GOLDFINGER_FILM}}** · codename
**{{GOLDFINGER_CODENAME}}** · version **{{GOLDFINGER_VERSION}}** ·
author **{{GOLDFINGER_AUTHOR}}** ({{GOLDFINGER_AFFILIATION}}).

Figures are referenced with Pandoc `{#fig:label}` anchors (see the figure
lines in `03_results.md`). No numeric result metric is hand-authored: every
value that can change with the reference intel is injected as a token.
