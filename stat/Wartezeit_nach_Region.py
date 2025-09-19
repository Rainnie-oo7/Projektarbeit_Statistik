import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.stats.api as sms

# === CSV laden ===
df = pd.read_csv("C:/Users/pathto/stat/warten_min_max_vorgespr.csv")

# Spalten, die ausgewertet werden sollen
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_min", "Gesetzlich_bis_Beh_Wartezeit_max",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_min", "Gesetzlich_bis_Vorgespräch_Wartezeit_max",
    "Vorgespräch_bis_Beh_min", "Vorgespräch_bis_Beh_max",
    "Privat_Wartezeit_min", "Privat_Wartezeit_max"
]

# === 1. Deskriptive Statistik ===
print("\n--- DESKRIPTIVE STATISTIK ---")
for sp in spalten:
    print(f"\nSpalte: {sp}")
    print(df[sp].describe(percentiles=[0.8, 0.85, 0.9]))    # GIbt nur die diskrete an wo die Werte bei 3/4 der Strecke liegen bei 75% Quantile. ALso nicht stochastisch. Völlig hirnrissig
    # df["Gesetzlich_Wartezeit_max"].describe(percentiles=[0.8, 0.85, 0.9])

# === 3. Boxplots für jede Spalte ===
plt.figure(figsize=(14,7))

# Farben: erst 6 dunkelgoldenrod, dann 2 steelblue
farben = ["darkgoldenrod"]*6 + ["steelblue"]*2

# Seaborn Boxplot
sns.boxplot(data=df[spalten], palette=farben)

plt.xticks(rotation=45, ha="right")
plt.ylabel("Wartezeit (Tage)")
plt.title("Wartezeiten Gastroskopie GKV/PKV")
plt.tight_layout()
plt.subplots_adjust(bottom=0.35)
plt.show()

"""
# === 2. Histogramme + KDE für jede Spalte ===
for sp in spalten:
    plt.figure(figsize=(10,5))
    sns.histplot(df[sp], bins=20, kde=True, color='skyblue')
    plt.title(f"Histogramm + KDE: {sp}")
    plt.xlabel("Wartezeit (Tage)")
    plt.ylabel("Anzahl")
    plt.show()
"""
"""
# === 4. Log-Normal Fit + MLE für jede Spalte ===
for sp in spalten:
    data = df[sp].dropna()
    if len(data) == 0:
        continue

    log_data = np.log(data[data > 0])  # nur positive Werte
    mu_hat, sigma_hat = stats.norm.fit(log_data)

    print(f"\n--- LOG-NORMAL MLE FIT: {sp} ---")
    print(f"μ (log-Mittel): {mu_hat:.4f}")
    print(f"σ (log-Stdabw.): {sigma_hat:.4f}")

    # Wahrscheinlichkeit für 25–35 Tage berechnen
    p_25_35 = stats.lognorm.cdf(35, s=sigma_hat, scale=np.exp(mu_hat)) - \
               stats.lognorm.cdf(25, s=sigma_hat, scale=np.exp(mu_hat))
    print(f"Wahrscheinlichkeit für 25–35 Tage: {p_25_35*100:.2f} %")

    # Plot
    plt.figure(figsize=(10,5))
    sns.histplot(data, bins=20, stat="density", color="skyblue", label="Daten")
    x_vals = np.linspace(1, data.max(), 500)
    pdf_vals = stats.lognorm.pdf(x_vals, s=sigma_hat, scale=np.exp(mu_hat))
    plt.plot(x_vals, pdf_vals, 'r-', lw=2, label="Gefittete Log-Normal")
    plt.title(f"Gefittete Log-Normal-Verteilung: {sp}")
    plt.xlabel("Wartezeit (Tage)")
    plt.ylabel("Dichte")
    plt.legend()
    plt.show()

# === 5. Optional: Mann-Whitney-U zwischen Regionen pro Spalte ===
# Beispiel:
# region1 = df[df["region"]=="Region1"][spalte]
# region2 = df[df["region"]=="Region2"][spalte]
# u_stat, p_val = stats.mannwhitneyu(region1.dropna(), region2.dropna())
# print(f"{spalte} U={u_stat:.2f}, p={p_val:.4f}")
"""