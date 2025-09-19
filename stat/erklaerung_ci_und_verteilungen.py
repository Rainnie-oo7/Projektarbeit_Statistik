import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# CSV laden
df = pd.read_csv("wartezeiten_min_max_vorgespr_region1.csv")
x = df["Gesetzlich_Wartezeit_min"].dropna().values

# Perzentile, die wir betrachten wollen
qs = np.array([0.10, 0.25, 0.50, 0.70, 0.80, 0.90])
B = 2000  # Bootstrap

# Kandidatenmodelle
cands = [
    ("lognorm", stats.lognorm, dict(floc=0)),
    ("gamma", stats.gamma, dict(floc=0)),
    ("weibull", stats.weibull_min, dict(floc=0))
]


# Funktion für Q und CI
def model_quantiles(dist, params, qs):
    return dist.ppf(qs, *params)


def parametric_bootstrap_cis(dist, params, qs, n, B=2000, rng=np.random.default_rng(42)):
    boots = np.empty((B, len(qs)))
    for b in range(B):
        xb = dist.rvs(*params, size=n, random_state=rng)
        qb = model_quantiles(dist, params, qs)
        boots[b, :] = qb
    lower = np.percentile(boots, 2.5, axis=0)
    upper = np.percentile(boots, 97.5, axis=0)
    return lower, upper


# Plot vorbereiten
plt.figure(figsize=(10, 6))

colors = {"lognorm": "blue", "gamma": "green", "weibull": "red"}

for name, dist, kw in cands:
    # Fit
    params = dist.fit(x, **kw)
    qhat = model_quantiles(dist, params, qs)
    ci_low, ci_high = parametric_bootstrap_cis(dist, params, qs, n=len(x), B=B)

    # Linie für Q_modell
    plt.plot(qs * 100, qhat, marker='o', color=colors[name], label=f"{name} Q_modell")

    # CI als Balken
    plt.fill_between(qs * 100, ci_low, ci_high, color=colors[name], alpha=0.2)

plt.xlabel("Quantil (%)")
plt.ylabel("Wartezeit (Tage)")
plt.title("Q_modell und 95%-CI für Gesetzlich_Wartezeit_min")
plt.legend()
plt.grid(True)
plt.show()
