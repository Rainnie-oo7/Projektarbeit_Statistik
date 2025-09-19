import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


df = pd.read_csv("warten_min_max_vorgespr_means_only.csv")

# --- Spalten und Quantile ---
# spalten = [
#     "Gesetzlich_bis_Beh_Wartezeit_min", "Gesetzlich_bis_Beh_Wartezeit_max",
#     "Gesetzlich_bis_Vorgespräch_Wartezeit_min", "Gesetzlich_bis_Vorgespräch_Wartezeit_max",
#     "Vorgespräch_bis_Beh_min", "Vorgespräch_bis_Beh_max",
#     "Privat_Wartezeit_min", "Privat_Wartezeit_max"
# ]
spalten = [
    "Gesetzlich_bis_Beh_Wartezeit_mean",
    "Gesetzlich_bis_Vorgespräch_Wartezeit_mean",
    "Vorgespräch_bis_Beh_mean",
    "Privat_Wartezeit_mean"
]

qs = np.array([0.10, 0.50, 0.70, 0.80, 0.85, 0.90, 0.95])
B = 2000  # Bootstrap-Replikate

# Kandidatenmodelle
cands = [
    ("lognorm", stats.lognorm, dict(floc=0), 2),
    ("gamma",   stats.gamma,   dict(floc=0), 2),
    ("weibull", stats.weibull_min, dict(floc=0), 2)
]

def model_quantiles(dist, params, qs):
    return dist.ppf(qs, *params)

def parametric_bootstrap_cis(dist, params, qs, n, B=2000, alpha=0.05, rng=np.random.default_rng(42)):
    boots = np.empty((B, len(qs)))
    for b in range(B):
        xb = dist.rvs(*params, size=n, random_state=rng)
        # Refit: optional, hier verzichten wir zur Vereinfachung auf Refit
        qb = model_quantiles(dist, params, qs)
        boots[b, :] = qb
    lower = np.percentile(boots, 100*alpha/2, axis=0)
    upper = np.percentile(boots, 100*(1-alpha/2), axis=0)
    return lower, upper

# --- Ergebnisse sammeln ---
rows = []

for sp in spalten:
    x = df[sp].dropna().values
    n = len(x)
    if n < 3:
        continue
    for name, dist, kw, kpars in cands:
        try:
            params = dist.fit(x, **kw)
            qhat = model_quantiles(dist, params, qs)
            ci_low, ci_high = parametric_bootstrap_cis(dist, params, qs, n, B=B)
            part = pd.DataFrame({
                "Spalte": sp,
                "Modell": name,
                "q": qs,
                "Q_modell": qhat,
                "CI_low": ci_low,
                "CI_high": ci_high
            })
            rows.append(part)
        except Exception:
            pass

parametrisch_tab_all = pd.concat(rows, ignore_index=True)

# --- In TXT speichern ---
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
with open("parametrische_perzentile_all_modelsbeideregionen.txt", "w", encoding="utf-8") as f:
    f.write("--- PARAMETRISCHE (stochastische) PERZENTILE für ALLE MODELLE ---\n\n")
    f.write(parametrisch_tab_all.round(2).to_string(index=False))

# --- Konsolen-Ausgabe ---
print("--- PARAMETRISCHE (stochastische) PERZENTILE für ALLE MODELLE ---")
print(parametrisch_tab_all.round(2).to_string(index=False))

# def plot_quantile_models(results, spalten):
#     for sp in spalten:
#         df_sp = results[results["Spalte"] == sp]
#         if df_sp.empty:
#             continue
#
#         plt.figure(figsize=(8, 5))
#         for model in df_sp["Modell"].unique():
#             sub = df_sp[df_sp["Modell"] == model]
#
#             # Modell-Quantile
#             plt.plot(sub["q"], sub["Q_modell"], marker="o", label=f"{model} Q")
#
#             # Konfidenzintervalle (als Band)
#             plt.fill_between(
#                 sub["q"], sub["CI_low"], sub["CI_high"],
#                 alpha=0.2, label=f"{model} CI"
#             )
#
#         plt.title(f"Quantile & CI für {sp}")
#         plt.xlabel("Quantile (q)")
#         plt.ylabel("Wartezeit")
#         plt.legend()
#         plt.grid(alpha=0.3)
#         plt.tight_layout()
#         plt.show()
#
#
# # Aufrufen
# plot_quantile_models(parametrisch_tab_all, spalten)

###################################################

# def plot_bar_quantiles(results, spalten, qtarget=0.5):
#     # Farben für Modelle
#     colors = {
#         "lognorm": "steelblue",
#         "gamma": "darkorange",
#         "weibull": "green"
#     }
#
#     # Kategorien vorbereiten
#     cats = spalten
#     x = np.arange(len(cats))
#     width = 0.25  # Balkenbreite (dünn)
#
#     fig, ax = plt.subplots(figsize=(12, 6))
#
#     # alle Modelle nebeneinander plotten
#     for i, model in enumerate(colors.keys()):
#         sub = results[(results["q"] == qtarget) & (results["Modell"] == model)]
#         means = []
#         lows = []
#         highs = []
#         for cat in cats:
#             row = sub[sub["Spalte"] == cat]
#             if not row.empty:
#                 means.append(row["Q_modell"].values[0])
#                 lows.append(row["CI_low"].values[0])
#                 highs.append(row["CI_high"].values[0])
#             else:
#                 means.append(np.nan)
#                 lows.append(np.nan)
#                 highs.append(np.nan)
#
#         ax.bar(
#             x + i*width - width,  # Versatz der Balken
#             means,
#             width=width,
#             color=colors[model],
#             label=model,
#             yerr=[np.array(means) - np.array(lows), np.array(highs) - np.array(means)],
#             capsize=4,
#             alpha=0.9
#         )
#
#     ax.set_xticks(x)
#     ax.set_xticklabels(cats, rotation=30, ha="right")
#     ax.set_ylabel("Wartezeit")
#     ax.set_title("Median-Wartezeiten (q=0.5) mit 95%-CI für alle Modelle")
#     ax.legend()
#     ax.grid(axis="y", alpha=0.3)
#
#     plt.tight_layout()
#     plt.show()
#
#
# # Aufrufen
# plot_bar_quantiles(parametrisch_tab_all, spalten, qtarget=0.5)

###############################################

def plot_bar_quantiles_stacked(results, spalten, qs_main=0.5, qs_high=[0.85, 0.9, 0.95]):
    # Farben fix
    colors = {
        "lognorm": "steelblue",
        "gamma": "darkorange",
        "weibull": "forestgreen"
    }

    cats = spalten
    x = np.arange(len(cats))
    width = 0.25  # Breite pro Modellgruppe

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, model in enumerate(colors.keys()):
        color = colors[model]

        # Median-Balken
        sub_median = results[(results["q"] == qs_main) & (results["Modell"] == model)]
        medians, lows, highs = [], [], []
        for cat in cats:
            row = sub_median[sub_median["Spalte"] == cat]
            if not row.empty:
                medians.append(row["Q_modell"].values[0])
                lows.append(row["CI_low"].values[0])
                highs.append(row["CI_high"].values[0])
            else:
                medians.append(np.nan)
                lows.append(np.nan)
                highs.append(np.nan)

        rects = ax.bar(
            x + i*width - width,  # Versatz pro Modell
            medians,
            width=width,
            color=color,
            alpha=0.9,
            label=f"{model} Median",
            yerr=[np.array(medians) - np.array(lows), np.array(highs) - np.array(medians)],
            capsize=4
        )

        # Hohe Quantile (gestapelt)
        for qtarget in qs_high:
            sub = results[(results["q"] == qtarget) & (results["Modell"] == model)]
            highs_q = []
            for cat in cats:
                row = sub[sub["Spalte"] == cat]
                highs_q.append(row["Q_modell"].values[0] if not row.empty else np.nan)

            rects_q = ax.bar(
                x + i*width - width,
                highs_q,
                width=width,
                color=color,
                alpha=0.3,
                label=f"{model} q={qtarget}" if i == 0 else None  # nur einmal in Legende
            )

            # Nur einmal pro Quantil beschriften
            for xi, h in zip(x, highs_q):
                if not np.isnan(h):
                    ax.text(
                        xi + i*width - width,
                        h,
                        f"{qtarget:.2f}",
                        ha="center", va="bottom",
                        fontsize=8
                    )

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=30, ha="right")
    ax.set_ylabel("Wartezeit")
    ax.set_title("Median und hohe Quantile (0.85, 0.90, 0.95) mit 95%-CI")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()


# Aufrufen
plot_bar_quantiles_stacked(parametrisch_tab_all, spalten, qs_main=0.5, qs_high=[0.85, 0.9, 0.95])
