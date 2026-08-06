# Results

## Market corner: price shock and convergence

Under the reference intel, removing {{MARKET_FRACTION_REMOVED}}% of the
floatable supply moves the equilibrium price from
${{MARKET_REFERENCE_PRICE}}$/oz to **${{MARKET_SHOCKED_PRICE}}$/oz**, a
**{{MARKET_PRICE_GAIN_PCT}}%** appreciation at elasticity
{{MARKET_ELASTICITY}}. Price approaches the shocked equilibrium geometrically
over the {{MARKET_STEPS}}-step tâtonnement window, ending at a relative
residual of {{MARKET_CONVERGENCE_RESIDUAL}} against a convergence tolerance of
{{MARKET_CONVERGENCE_TOLERANCE}} (converged: {{MARKET_CONVERGED}}). Tâtonnement
reaches $P^*$ only in the limit, so convergence is asserted against that
tolerance rather than by exact equality.

![Operation Grand Slam: tatonnement price trajectory toward the shocked equilibrium.](output/figures/market_corner_trajectory.png){#fig:corner}

The figure shows the reference price, the shocked equilibrium price, and the
deterministic adjustment path. The corner is economically self-reinforcing:
a larger sterilized fraction yields a higher equilibrium, which in turn
raises the value of the seized stockpile.

## Vault defense: layered score and penetration

The {{VAULT_LAYER_COUNT}} concentric layers of the reference vault score
**{{VAULT_SCORE}}** — classified **{{VAULT_VERDICT}}** security — with an
overall sequential-penetration probability of
**{{VAULT_PENETRATION_PCT}}%**. The weakest layer is the
**{{VAULT_WEAKEST}}**, which is where fortification yields the greatest
marginal composite gain.

![Fort Knox-style layered defense: per-layer ratings and composite defense-in-depth score.](output/figures/vault_layered_score.png){#fig:vault}

## Vault network: penetration and hardening

The network model locates the vault's true weak point. Across the
{{VAULT_ZONE_COUNT}}-zone graph, the minimum-effort intrusion path from the
perimeter to the gold chamber is **{{VAULT_MIN_EFFORT}}** effort and runs
through the **secret tunnel** ({{VAULT_WEAK_PATH_EDGES}} zone transitions),
bypassing the costly guarded spine. {{VAULT_CRITICAL_EDGES}} edges are
critical — removing each one forces a strictly costlier route. Spending the
{{VAULT_HARDENING_BUDGET}}-unit hardening budget at {{VAULT_GAIN_PER_UNIT}}
effort per unit raises the minimum required intrusion effort from
{{VAULT_MIN_EFFORT}} to **{{VAULT_HARDENED_EFFORT}}** (a lift of
{{VAULT_EFFORT_RAISED}}), closing off the tunnel as the free ride. The
allocation is greedy rather than exactly optimal, so its lift is normally a
lower bound on what the same budget could buy; here the bound is *measured*,
not just disclaimed. At a small verification budget of
{{VAULT_VERIFY_BUDGET}} units we enumerate every allocation of that budget
across the graph's edges and confirm the greedy result achieves the maximum
achievable lift ({{VAULT_VERIFY_OPTIMAL_LIFT}}, greedy matches optimal:
{{VAULT_GREEDY_MATCHES_OPTIMAL}}), so on this graph the greedy allocation is
exactly optimal at small budgets.

![Vault network: minimum-effort intrusion path through the secret tunnel, before and after hardening.](output/figures/vault_network.png){#fig:vault_net}

## Macroeconomic attack: speculative reserve drain

The speculative-attack model turns gold accumulation into a monetary weapon.
With the reference intel the shadow floating rate crosses parity at
{{RESERVE_ATTACK_TIME}} time units, forcing the peg's collapse **before** the
gradual reserve floor at {{RESERVE_FLOOR_TIME}} (suddenness
{{RESERVE_ATTACK_SUDDENNESS}}), and the subsequent float depreciates the
currency by **{{RESERVE_DEPRECIATION_PCT}}%**.

![Speculative attack on the gold peg: reserve drain and attack time.](output/figures/reserve_crisis.png){#fig:reserve_crisis}

## Laser threat: burn-through time

At {{LASER_POWER_W}} W the reference steel plate
({{LASER_THICKNESS_MM}} mm) is breached in **{{LASER_BURN_THROUGH_S}} s**,
denoted a **{{LASER_SEVERITY}}** threat against the
{{LASER_SEVERITY_THRESHOLD_W}} W mission threshold. Doubling
power halves burn-through time; doubling thickness doubles it, so the
defensive levers on the laser side are plate thickness and material (higher
$\rho c \Delta T$).

![Laser threat physics: burn-through time vs beam power for the reference vault plate.](output/figures/laser_burn_through.png){#fig:laser}

## Laser thermal engagement: beam focus and heat conduction

Accounting for Gaussian divergence and heat conduction, the reference beam
melts the plate surface at focus in {{LASER_FOCUS_MELT_S}} s and retains an
effective engagement range of **{{LASER_EFFECTIVE_RANGE_M}} m** within the
{{LASER_THREAT_WINDOW_S}} s threat window (Rayleigh range
{{LASER_RAYLEIGH_RANGE_M}} m, focus waist {{LASER_WAIST_MM}} mm). Defocusing
with range lengthens melt time, so a defender pushing the engagement beyond the
Rayleigh range materially degrades the threat.

![Laser engagement: surface melt time grows as the Gaussian beam defocuses with distance.](output/figures/laser_engagement.png){#fig:laser_engagement}

All {{GOLDFINGER_MODULE_COUNT}} model results above are computed by the pure
domain core and injected here as generated variables — none is typed by hand,
including the counts in this sentence. Re-running the pipeline reproduces
identical numbers from the module `REFERENCE_*` constants.

The no-hardcoding claim is gated, with a stated limit. Every computed result
token is classified, and each one whose value is a numeric literal of at least
three characters is searched for in the rendered prose (the numbered sections
and `preamble.md`), with a positive control that pastes each value in turn and
confirms the scan flags it. The remaining computed tokens — bare small integers
such as the module and layer counts, and categorical words such as the vault
verdict and the laser severity — **are not scanned**, because searching prose
for `6` or `medium` finds ordinary English rather than a pasted result. Those
tokens are listed explicitly in the test with the reason, and a further test
asserts the list is exactly what the rule rejects, so the hole cannot widen
silently. It is a real hole nonetheless: a hand-typed module count in this
prose would not be caught by the scan.
