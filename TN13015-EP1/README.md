# TN13015-EP1: Boltzmann constant (fit check)

Read-only copy and check of `RikvDam/TN13015-Rik-Jan-EP1` (commit `5d0cd3b`). Nothing in that repo was changed.

- `fit_ex6.py`: rewrite of `fit-ex6.py`, using the real data and the notebook's processing; n = 2.0 ± 0.1 is taken as given (BM.md, line 39).
- `data/`: unchanged copies of `DATA/metingenboltzman.csv` and `DATA/metingenR.csv`.
- `plot_metingen.png`, `plot_fit.png`, `plot_residuen.png`: output of the script.

Run: `python fit_ex6.py`

## Result

kB = (1.35 ± 0.07)e-23 J/K, compared with 1.380649e-23 (exact). That is a 0.4σ difference, dominated by u(n) (5%).

## Fixes compared with the first version

1. The uncertainty in U_D is now included in the fit (effective variance). χ²_red went from 2.43 to 0.30.
2. The range (0.066 to 0.428 V, while the manual asks for 0.1 to 0.6 V) is printed. A fit on U_D ≥ 0.1 V only gives kB = 1.352e-23, so it makes no difference.
3. The meter percentage (0.1% or 0.3%) is now one variable. It changes kB by about 0.1%, which is negligible. 0.3% is used. **Still check it in the meter manual.**
4. The uncertainty in R1 is not added per point, on purpose: it scales all currents and only ends up in I0, not in b. A 1% change in R1 changes kB by 0.006%.

## Open

- χ²_red = 0.30 < 1 means the error bars are probably too large. The suspect is the 1.5% on the 5.5 DMM, which seems large for that meter. Check it in its manual.
- The residuals show a clear S-shaped pattern, not scatter, so the model does not describe the data perfectly.
