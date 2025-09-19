import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# === Einstellungen ===
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit_mean",
]

max_days = 316
max_weeks = max_days // 7  # ≈ 45 Wochen
intervalle = [(0, 4), (4, 8), (8, 12), (12, 16)]
intervalle.append((16, max_weeks))  # Letztes Intervall: 16+ Wochen

# Modelle
cands = [
    ("lognorm", stats.lognorm, dict(floc=0)),
    ("gamma", stats.gamma, dict(floc=0)),
    ("weibull", stats.weibull_min, dict(floc=0)),
]

B = 2000  # Bootstrap-Replikate

# === Hilfsfunktion ===
def berechne_bootstrap_wahrscheinlichkeiten(x, intervals, B=2000, max_days=316):
    """Berechne Intervallwahrscheinlichkeiten mit Bootstrap für Population"""
    results = []
    for name, dist, kw in cands:
        try:
            # Parameter schätzen
            params = dist.fit(x, **kw)

            # Bootstrap
            probs_boot = []
            for b in range(B):
                xb = dist.rvs(*params, size=len(x))
                probs_b = []
                for a, b_int in intervals:
                    a_days = a * 7
                    b_days = b_int * 7
                    if b_days > max_days:
                        b_days = max_days
                    p = dist.cdf(b_days, *params) - dist.cdf(a_days, *params)
                    probs_b.append(p)
                probs_boot.append(probs_b)
            probs_boot = np.array(probs_boot)

            # Mittelwert und 95%-CI
            mean_probs = probs_boot.mean(axis=0)
            ci_low = np.percentile(probs_boot, 2.5, axis=0)
            ci_high = np.percentile(probs_boot, 97.5, axis=0)

            # Speichern
            intervall_names = [f"{a}-{b} Wochen" if b*7 <= max_days else f"{a}-{b} Wochen (gedeckelt)" for a, b in intervals]
            results.append((name, intervall_names, mean_probs, ci_low, ci_high))

        except Exception as e:
            print(f"Fehler bei {name}: {e}")
    return results

# === CSV einlesen ===
df = pd.read_csv("warten_min_max_vorgespr_means_only.csv", sep=",")
df.columns = df.columns.str.strip()

ergebnis = []

for _, row in df.iterrows():
    nummer = row.get("Nummer", None)
    for spalte in spalten:
        x = df[spalte].dropna().values
        if len(x) < 3:
            continue

        model_results = berechne_bootstrap_wahrscheinlichkeiten(x, intervalle, B=B)

        # Mittelwert über alle Modelle
        intervall_names = model_results[0][1]
        mean_probs_models = np.mean([res[2] for res in model_results], axis=0)
        ci_low_models = np.mean([res[3] for res in model_results], axis=0)
        ci_high_models = np.mean([res[4] for res in model_results], axis=0)

        for iv_name, p_mean, ci_l, ci_h in zip(intervall_names, mean_probs_models, ci_low_models, ci_high_models):
            ergebnis.append({
                "Nummer": nummer,
                "Spalte": spalte,
                "Intervall": iv_name,
                "Wahrscheinlichkeit_Mittel": p_mean,
                "CI_low": ci_l,
                "CI_high": ci_h
            })

# === CSV schreiben ===
df_out = pd.DataFrame(ergebnis)
df_out.to_csv("wartezeiten_wahrscheinlichkeiten_population_bootstrap.csv", sep=";", index=False)
print("Fertig: wartezeiten_wahrscheinlichkeiten_population_bootstrap.csv")

# === Plot Beispiel ===
def plot_spalte(spalte):
    plt.figure(figsize=(10, 6))
    subset = df_out[df_out["Spalte"] == spalte]
    intervals = list(dict.fromkeys(subset["Intervall"]))
    x_pos = np.arange(len(intervals))

    y = [subset[subset["Intervall"] == iv]["Wahrscheinlichkeit_Mittel"].mean() for iv in intervals]
    yerr_low = [subset[subset["Intervall"] == iv]["CI_low"].mean() for iv in intervals]
    yerr_high = [subset[subset["Intervall"] == iv]["CI_high"].mean() for iv in intervals]
    # yerr = [np.array(y) - np.array(yerr_low), np.array(yerr_high) - np.array(y)]

    yerr_low = [max(0, y_i - l) for y_i, l in zip(y, yerr_low)]
    yerr_high = [max(0, h - y_i) for y_i, h in zip(y, yerr_high)]
    yerr = [yerr_low, yerr_high]

    plt.bar(x_pos, y, width=0.5, color="steelblue", alpha=0.7, yerr=yerr, capsize=4)

    plt.bar(x_pos, y, width=0.5, color="steelblue", alpha=0.7, yerr=yerr, capsize=4)
    plt.xticks(x_pos, intervals, rotation=45)
    plt.ylabel("Wahrscheinlichkeit")
    plt.title(f"Wahrscheinlichkeiten je Intervall - Gesetzlich - Von Kontaktaufnahme bis Behandlung")
    # plt.title(f"Wahrscheinlichkeiten je Intervall - Gesetzlich - Von Kontaktaufnahme bis Vorgespräch")
    # plt.title(f"Wahrscheinlichkeiten je Intervall - Gesetzlich - Von Vorgespräch bis Behandlung")
    # plt.title(f"Wahrscheinlichkeiten je Intervall - Privat - Von Kontaktaufnahme bis Behandlung")
    plt.tight_layout()
    plt.show()


# Beispielplot
# plot_spalte("Gesetzlich_bis_Beh_Wartezeit_mean")
# plot_spalte("Gesetzlich_bis_Vorgespräch_Wartezeit_mean")
# plot_spalte("Vorgespräch_bis_Beh_mean")
# plot_spalte("Privat_Wartezeit_mean")
