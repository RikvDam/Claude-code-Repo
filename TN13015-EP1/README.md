# TN13015-EP1: Boltzmann constant (fit check)

Read-only copy and check of `RikvDam/TN13015-Rik-Jan-EP1` (commit `5d0cd3b`). Nothing in that repo was changed.

- `fit_ex6.py`: rewrite of `fit-ex6.py`, using the real data and the notebook's processing; n = 2.0 ± 0.1 is taken as given (BM.md, line 39).
- `data/`: unchanged copies of `DATA/metingenboltzman.csv` and `DATA/metingenR.csv`.
- `plot_metingen.png`, `plot_fit.png`: output of the script.

Run: `python fit_ex6.py`

Result: kB = (1.34 ± 0.07)e-23 J/K, χ²_red = 2.43, 70 points, U_D from 0.066 to 0.43 V.
