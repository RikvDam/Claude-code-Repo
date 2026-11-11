import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Herschreven versie van fit-ex6.py, nu met de echte metingen uit DATA/.
# Volgorde zoals de handleiding vraagt: ruwe data / bewerkte data / plot / fit.

map_hier = os.path.dirname(os.path.abspath(__file__))
map_data = os.path.join(map_hier, "data")

# Constanten
q = -1.602176634e-19      # C, lading elektron (negatief, zie BM.md)
T, uT = 295.0, 1.0        # K, kamertemperatuur (geschat)

# Idealiteitsfactor: GEGEVEN in de handleiding, niet gemeten.
# BM.md: "n is de idealiteitsfactor ... n = 2.0 +- 0.1 voor Si"
n, un = 2.0, 0.1

# Weerstanden, gemeten met de 5.5 digit DMM (DATA/metingenR.csv)
R1 = 10021.7              # Ohm, in serie met de diode
R2 = 4673.3               # Ohm, spanningsdeler
R3 = 328.27               # Ohm, spanningsdeler

# Ruwe data
V_Bron, V_Weerstand = np.loadtxt(os.path.join(map_data, "metingenboltzman.csv"),
                                 delimiter=",", skiprows=1, unpack=True)
V_Weerstand = V_Weerstand / 1000          # mV -> V (csv staat in mV)

# Onzekerheden meters
# TODO: beide percentages nog controleren in de handleidingen van de meters.
# Oude commentaar zei 0.1%, oude code 0.3%. Getest: 0.1% of 0.3% verandert kB met ~0.1%,
# dat is verwaarloosbaar t.o.v. de 5% van n. Hier de ruimste (0.3%) aangehouden.
procent_bron = 0.003                                                    # 3.5 DMM
uV_Bron = V_Bron * procent_bron + np.where(V_Bron < 4, 0.001, 0.01)    # V (+1 digit: 1 mV / 10 mV)
uV_Weerstand = V_Weerstand * 0.015 + 0.000006                           # V, 5.5 DMM

# Bewerkte data
f = R3 / (R2 + R3)              # spanningsdeler: U = f * U_bron
R_th = R2 * R3 / (R2 + R3)      # Thevenin-weerstand van de spanningsdeler

I_D = V_Weerstand / R1
U_D = f * V_Bron - V_Weerstand - I_D * R_th

u_UD = np.sqrt((f * uV_Bron) ** 2 + ((1 + R_th / R1) * uV_Weerstand) ** 2)
u_ID = uV_Weerstand / R1

# Onzekerheid in R1 zit NIET in u_ID, met opzet:
# een fout in R1 schaalt ALLE stromen met dezelfde factor. In I = I0 * (exp(bU) - 1)
# komt dat alleen in I0 terecht, niet in b. kB hangt dus niet af van R1.
# (Getest: R1 1% anders -> kB verandert 0.006%.) Hem per punt optellen zou de
# foutbalken te groot maken, want het is geen toevallige fout per punt.

# Meetbereik: de handleiding vraagt U_D van 0.1 V tot 0.6 V.
print(f"U_D loopt van {U_D.min():.3f} V tot {U_D.max():.3f} V ({len(U_D)} punten)")
print("Let op: boven 0.43 V is niet gemeten, onder 0.1 V wel (6 punten).")

# Plot 1: metingen
plt.figure()
plt.errorbar(U_D, I_D, xerr=u_UD, yerr=u_ID, fmt="o", markersize=3)
plt.yscale("log")
plt.xlabel("$U_D$ (V)")
plt.ylabel("$I_D$ (A)")
plt.title("Metingen")
plt.savefig(os.path.join(map_hier, "plot_metingen.png"), dpi=150)
plt.show()

# Fitten, vgl. (eq:stroom_diode): I = I0 * (exp(b*U) - 1) met b = -q / (n kB T)
def model(U, I0, b):
    return I0 * np.expm1(b * U)

# curve_fit gebruikt alleen de foutbalken in y (I_D). De onzekerheid in U_D tellen we
# mee met de "effectieve variantie": u_eff^2 = u_I^2 + (dI/dU * u_U)^2.
# dI/dU hangt van de fit af, dus een paar keer herhalen tot het niet meer verandert.
popt, pcov = curve_fit(model, U_D, I_D, p0=[1e-9, 20], sigma=u_ID, absolute_sigma=True)
for i in range(5):
    I0, b = popt
    dI_dU = I0 * b * np.exp(b * U_D)
    u_eff = np.sqrt(u_ID ** 2 + (dI_dU * u_UD) ** 2)
    popt, pcov = curve_fit(model, U_D, I_D, p0=popt, sigma=u_eff, absolute_sigma=True)

I0, b = popt
uI0, ub = np.sqrt(np.diag(pcov))

# Hoe goed is de fit? chi^2 gedeeld door vrijheidsgraden zou rond 1 moeten liggen.
residuen = (I_D - model(U_D, *popt)) / u_eff
chi2_red = np.sum(residuen ** 2) / (len(U_D) - len(popt))

# Plot 2: metingen + fit
plt.figure()
U_lijn = np.linspace(U_D.min(), U_D.max(), 300)
plt.errorbar(U_D, I_D, xerr=u_UD, yerr=u_ID, fmt="o", markersize=3, label="metingen")
plt.plot(U_lijn, model(U_lijn, *popt), label="fit")
plt.yscale("log")
plt.xlabel("$U_D$ (V)")
plt.ylabel("$I_D$ (A)")
plt.legend()
plt.title("Metingen + fit")
plt.savefig(os.path.join(map_hier, "plot_fit.png"), dpi=150)
plt.show()

# Plot 3: residuen. Bij een goede fit liggen ze willekeurig rond 0, zonder patroon.
plt.figure()
plt.plot(U_D, residuen, "o", markersize=3)
plt.axhline(0, color="k")
plt.xlabel("$U_D$ (V)")
plt.ylabel("(meting - fit) / $u_{eff}$")
plt.title("Residuen")
plt.savefig(os.path.join(map_hier, "plot_residuen.png"), dpi=150)
plt.show()

# Controle: fit alleen op het bereik uit de handleiding (U_D >= 0.1 V)
binnen = U_D >= 0.1
popt2, pcov2 = curve_fit(model, U_D[binnen], I_D[binnen], p0=popt,
                         sigma=u_eff[binnen], absolute_sigma=True)
kB_binnen = -q / (popt2[1] * n * T)

# Boltzmann-constante: kB = -q / (b n T)
kB = -q / (b * n * T)
u_kB = kB * np.sqrt((ub / b) ** 2 + (un / n) ** 2 + (uT / T) ** 2)

print(f"I0 = ({I0:.3e} +- {uI0:.1e}) A")
print(f"b  = ({b:.3f} +- {ub:.3f}) 1/V")
print(f"chi2_red = {chi2_red:.2f}")
print(f"relatieve bijdragen: b {ub/b:.1%}, n {un/n:.1%}, T {uT/T:.1%}")
print(f"kB = ({kB:.2e} +- {u_kB:.1e}) J/K")
print(f"kB alleen U_D >= 0.1 V: {kB_binnen:.3e} J/K")
print("literatuur: kB = 1.380649e-23 J/K (exact, SI 2019)")
