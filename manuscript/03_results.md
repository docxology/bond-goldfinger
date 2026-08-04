# Results

## Market corner: price shock and convergence

Under the reference intel, removing {{MARKET_FRACTION_REMOVED}}% of the
floatable supply moves the equilibrium price from
${{MARKET_REFERENCE_PRICE}}$/oz to **${{MARKET_SHOCKED_PRICE}}$/oz**, a
**{{MARKET_PRICE_GAIN_PCT}}%** appreciation at elasticity
{{MARKET_ELASTICITY}}. Price converges to the shocked equilibrium over the
tatonnement window (converged: {{MARKET_CONVERGED}}).

![Operation Grand Slam: tatonnement price trajectory toward the shocked equilibrium.](output/figures/market_corner_trajectory.png){#fig:corner}

The figure shows the reference price, the shocked equilibrium price, and the
deterministic adjustment path. The corner is economically self-reinforcing:
a larger sterilized fraction yields a higher equilibrium, which in turn
raises the value of the seized stockpile.

## Vault defense: layered score and penetration

The six concentric layers of the reference vault score **{{VAULT_SCORE}}** —
classified **{{VAULT_VERDICT}}** security — with an overall penetration
probability of **{{VAULT_PENETRATION_PCT}}%**. The weakest layer is the
**{{VAULT_WEAKEST}}**, which is where fortification yields the greatest
marginal composite gain.

![Fort Knox-style layered defense: per-layer ratings and composite defense-in-depth score.](output/figures/vault_layered_score.png){#fig:vault}

## Laser threat: burn-through time

At {{LASER_POWER_W}} W the reference steel plate
({{LASER_THICKNESS_MM}} mm) is breached in **{{LASER_BURN_THROUGH_S}} s**,
denoted a **{{LASER_SEVERITY}}** threat at the mission threshold. Doubling
power halves burn-through time; doubling thickness doubles it, so the
defensive levers on the laser side are plate thickness and material (higher
$\rho c \Delta T$).

![Laser threat physics: burn-through time vs beam power for the reference vault plate.](output/figures/laser_burn_through.png){#fig:laser}

The three results are computed by the pure domain core and injected here as
generated variables; re-running the pipeline reproduces identical numbers
versus the single deterministic source of truth.
