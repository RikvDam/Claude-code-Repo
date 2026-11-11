import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Herschreven versie van fit-ex6.py, nu met de echte metingen uit DATA/.
# Volgorde zoals de handleiding vraagt: ruwe data / bewerkte data / plot / fit.

map_data = os.path.join(os.path.dirname(__file__), "data")

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
# TODO: uR1 uit de specificaties van de 5.5 DMM halen (handleiding meter)

# Ruwe data
V_Bron, V_Weerstand = np.loadtxt(os.path.join(map_data, "metingenboltzman.csv"),
                                 delimiter=",", skiprows=1, unpack=True)
V_Weerstand = V_Weerstand / 1000          # mV -> V (csv staat in mV)

# Onzekerheden meters, overgenomen uit het labjournaal
# TODO: commentaar zei 0.1%, code zegt 0.3%. Check in de handleiding van de 3.5 DMM.
uV_Bron = V_Bron * 0.003 + np.where(V_Bron < 4, 0.001, 0.01)   # V, 3.5 DMM
uV_Weerstand = V_Weerstand * 0.015 + 0.000006                  # V, 5.5 DMM

# Bewerkte data
f = R3 / (R2 + R3)              # spanningsdeler: U = f * U_bron
R_th = R2 * R3 / (R2 + R3)      # Thevenin-weerstand van de spanningsdeler

I_D = V_Weerstand / R1
U_D = f * V_Bron - V_Weerstand - I_D * R_th

u_UD = np.sqrt((f * uV_Bron) ** 2 + ((1 + R_th / R1) * uV_Weerstand) ** 2)
u_ID = uV_Weerstand / R1        # onzekerheid in R1 nog verwaarloosd (zie TODO)

# Plot 1: metingen
plt.errorbar(U_D, I_D, xerr=u_UD, yerr=u_ID, fmt="o", markersize=3)
plt.yscale("log")
plt.xlabel("$U_D$ (V)")
plt.ylabel("$I_D$ (A)")
plt.title("Metingen")
plt.savefig(os.path.join(os.path.dirname(__file__), "plot_metingen.png"), dpi=150)
plt.show()

# Fitten, vgl. (eq:stroom_diode): I = I0 * (exp(b*U) - 1) met b = -q / (n kB T)
def model(U, I0, b):
    return I0 * np.expm1(b * U)

popt, pcov = curve_fit(model, U_D, I_D, p0=[1e-9, 20], sigma=u_ID, absolute_sigma=True)
I0, b = popt
uI0, ub = np.sqrt(np.diag(pcov))

# Hoe goed is de fit? chi^2 gedeeld door vrijheidsgraden zou rond 1 moeten liggen.
residuen = (I_D - model(U_D, *popt)) / u_ID
chi2_red = np.sum(residuen ** 2) / (len(U_D) - len(popt))

# Plot 2: metingen + fit
U_lijn = np.linspace(U_D.min(), U_D.max(), 300)
plt.errorbar(U_D, I_D, xerr=u_UD, yerr=u_ID, fmt="o", markersize=3, label="metingen")
plt.plot(U_lijn, model(U_lijn, *popt), label="fit")
plt.yscale("log")
plt.xlabel("$U_D$ (V)")
plt.ylabel("$I_D$ (A)")
plt.legend()
plt.title("Metingen + fit")
plt.savefig(os.path.join(os.path.dirname(__file__), "plot_fit.png"), dpi=150)
plt.show()

# Boltzmann-constante: kB = -q / (b n T)
kB = -q / (b * n * T)
u_kB = kB * np.sqrt((ub / b) ** 2 + (un / n) ** 2 + (uT / T) ** 2)

# Welke term domineert de onzekerheid?
print(f"I0 = ({I0:.3e} +- {uI0:.1e}) A")
print(f"b  = ({b:.3f} +- {ub:.3f}) 1/V")
print(f"chi2_red = {chi2_red:.2f}")
print(f"relatieve bijdragen: b {ub/b:.1%}, n {un/n:.1%}, T {uT/T:.1%}")
print(f"kB = ({kB:.2e} +- {u_kB:.1e}) J/K")
print("literatuur: kB = 1.380649e-23 J/K (exact, SI 2019)")
