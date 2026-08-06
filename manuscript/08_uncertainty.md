# Uncertainty and Sensitivity

The models return point estimates from a single reference intel vector. This
section quantifies how those headline numbers move when the unobservable
inputs shift, because a number without a sensitivity context reads as more
certain than it is.

## Market corner: elasticity sensitivity

The corner's price gain is the quantity most exposed to the (unobservable)
demand elasticity: the shocked price is
$P^* = P_0\,(S_0/S_{\text{eff}})^{1/\eta}$, so the *exponent* is $1/\eta$ and
the gain is exponentially sensitive to $\eta$. At the reference elasticity
the gain is **{{MARKET_PRICE_GAIN_PCT}}%**. Because $\eta$ is an analyst
input, we evaluate the model at $\pm 10\%$ around it:

- $\eta$ reduced 10% (more elastic demand reacting less to the shock): gain
  **{{MARKET_GAIN_PCT_LOW_ELASTICITY}}%**
- $\eta$ raised 10% (steeper demand reacting more): gain
  **{{MARKET_GAIN_PCT_HIGH_ELASTICITY}}%**

The swing is asymmetric in the *direction that hurts the corner*: a 10% error
in the elasticity assumption moves the headline by more than a third of its
own value. Any decision that leans on the absolute gain figure — rather than
on the direction and the shock itself — should carry this band.

## Laser burn-through: the $1/P$ lever

The energy-balance burn-through time is exactly proportional to
$1/P_\text{abs} = 1/(aP)$, so any power-assumption error maps directly:
doubling power halves the time (from **{{LASER_BURN_THROUGH_S}} s** to
**{{LASER_BURN_DOUBLE_POWER_S}} s**), and halving the (unobservable)
absorptivity doubles it. The time carries the *inverse* of the power error,
so it is not robust to absorptivity misspecification. This is a structural,
parameter-free statement — it holds for any positive power and absorptivity
in this model — so it is a property of the physics, not of the reference
intel.

## Vault hardening: the greedy gap is measured

The one place an approximation matters is the hardening allocation. Rather
than disclaim an unmeasured lower bound, the package enumerates every
allocation of a small verification budget ({{VAULT_VERIFY_BUDGET}} units)
across the graph and reports the exhaustive optimum
({{VAULT_VERIFY_OPTIMAL_LIFT}} lift; greedy matches optimal:
{{VAULT_GREEDY_MATCHES_OPTIMAL}}). On the reference graph the greedy
allocation is exactly optimal at that budget; this is a measured fact here,
not a general theorem, which is precisely why the enumeration exists.

## What the numbers are not

These are single-point, single-intel outputs of deliberately stylized models
(full scope in [scope and related work](07_scope_and_related_work.md)). The
uncertainty quantified above is *within*-model sensitivity to declared inputs;
it does not capture the (larger, unquantifiable) model-form uncertainty — the
gap between these laws and the real market, vault, or laser. Presenting both
— a headline and its within-model band, side by side with the scope boundary
— is the honest shape of the result.
