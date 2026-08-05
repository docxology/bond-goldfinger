# References

Each model in this package implements a published result rather than an
invented one; `references.bib` is the machine-readable form of the list below,
and the notes name the function each source backs.

## Market corner

[1] L. Walras, *Éléments d'économie politique pure, ou théorie de la richesse
sociale*. Lausanne: L. Corbaz & Cie, 1874. — Origin of the tâtonnement
price-adjustment process driving `market_attack.simulate_corner`.

[2] J. R. Hicks, *Value and Capital*, 2nd ed. Oxford: Oxford University Press,
1946. — Constant-elasticity demand and market clearing behind the shocked
equilibrium price.

[3] A. S. Kyle, "Continuous auctions and insider trading," *Econometrica*,
vol. 53, no. 6, pp. 1315–1335, 1985. — The price impact of a strategic
trader; the microstructure counterpart to the corner's sterilizing supply
shock, and the reason the closed form here is a deliberate abstraction.

## Speculative attack on the gold peg

[4] P. Krugman, "A model of balance-of-payments crises," *Journal of Money,
Credit and Banking*, vol. 11, no. 3, pp. 311–325, 1979. — The
first-generation speculative-attack setup underlying `reserve_attack`.

[5] R. P. Flood and P. M. Garber, "Collapsing exchange-rate regimes: some
linear examples," *Journal of International Economics*, vol. 17, no. 1–2,
pp. 1–13, 1984. — The linear shadow-rate and attack-time closed forms
implemented in `reserve_attack.attack_time` and `reserve_floor_time`.

## Vault defense — layered and network

[6] M. L. Garcia, *The Design and Evaluation of Physical Protection Systems*,
2nd ed. Burlington, MA: Butterworth-Heinemann, 2007. — Layered physical
protection, adversary sequence diagrams, and detection/delay path analysis;
the standard reference behind both `vault_security` (weighted layer scoring,
sequential penetration) and `vault_threat_network` (the adversary path as a
weighted graph).

[7] E. W. Dijkstra, "A note on two problems in connexion with graphs,"
*Numerische Mathematik*, vol. 1, pp. 269–271, 1959. — The shortest-path
algorithm behind `minimum_effort_path`.

[8] E. Israeli and R. K. Wood, "Shortest-path network interdiction,"
*Networks*, vol. 40, no. 2, pp. 97–111, 2002. — The shortest-path
interdiction / improvement problem that `harden_network` approximates with a
greedy marginal-gain allocation.

## Laser threat — scalar and thermal

[9] W. M. Steen and J. Mazumder, *Laser Material Processing*, 4th ed. London:
Springer, 2010. — Continuous-wave energy-balance and cutting models behind
`laser_physics.burn_through_time`.

[10] H. S. Carslaw and J. C. Jaeger, *Conduction of Heat in Solids*, 2nd ed.
Oxford: Oxford University Press, 1959. — The constant-surface-flux
semi-infinite-solid solution used by `laser_thermal.surface_melt_time`.

[11] A. E. Siegman, *Lasers*. Mill Valley, CA: University Science Books, 1986.
— Gaussian-beam propagation, waist, and Rayleigh range used by
`laser_thermal.spot_radius_at_distance`.

## Protocol

[12] PROJECT BOND suite, "BOND-API: the frozen `MissionProvider` protocol,"
`bond-api` package, 2026. — The mission contract this film package implements
(brief / recon / plan / execute / debrief).
