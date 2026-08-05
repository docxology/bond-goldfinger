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

## Vault network: penetration and hardening

The network model locates the vault's true weak point. The minimum-effort
intrusion path from the perimeter to the gold chamber is
**{{VAULT_MIN_EFFORT}}** effort and runs through the **secret tunnel**
({{VAULT_WEAK_PATH_EDGES}} zone transitions), bypassing the costly guarded
spine. {{VAULT_CRITICAL_EDGES}} edges are critical — removing or hardening them
forces a far costlier route. A {{VAULT_EFFORT_RAISED}}-effort hardening budget
raises the minimum required intrusion effort from {{VAULT_MIN_EFFORT}} to
**{{VAULT_HARDENED_EFFORT}}**, closing off the tunnel as the free ride.

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
denoted a **{{LASER_SEVERITY}}** threat at the mission threshold. Doubling
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

The six results are computed by the pure domain core and injected here as
generated variables; re-running the pipeline reproduces identical numbers
versus the single deterministic source of truth.
