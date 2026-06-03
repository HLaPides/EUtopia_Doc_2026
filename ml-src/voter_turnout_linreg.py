import numpy as np
import pandas as pd
from scipy import stats

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv("../datasets/eu_turnout_clean.csv")

FEATURES = [
    "gdp_per_capita",
    "unemployment_rate",
    "compulsory_voting",
    "years_eu_membership",
    "urbanization_rate",
    "median_age",
    "eu_net_beneficiary",
    "weekend_voting",
    "national_turnout",
]
TARGET = "voter_turnout"

X = df[FEATURES].values
y = df[TARGET].values

# ── Standardise features (zero mean, unit variance) ───────────────────────────
X_mean = X.mean(axis=0)
X_std  = X.std(axis=0)
X_std[X_std == 0] = 1          # guard against constant columns
X_scaled = (X - X_mean) / X_std

# ── OLS via normal equations ───────────────────────────────────────────────────
X_int = np.column_stack([np.ones(len(X_scaled)), X_scaled])   # add intercept
coeffs, _, _, _ = np.linalg.lstsq(X_int, y, rcond=None)

# ── Model metrics ──────────────────────────────────────────────────────────────
y_pred  = X_int @ coeffs
ss_res  = np.sum((y - y_pred) ** 2)
ss_tot  = np.sum((y - y.mean()) ** 2)
r2      = 1 - ss_res / ss_tot

n, p    = X_int.shape
mse     = ss_res / (n - p)
rmse    = np.sqrt(mse)

# ── Standard errors, t-stats, p-values ────────────────────────────────────────
cov      = mse * np.linalg.inv(X_int.T @ X_int)
se       = np.sqrt(np.diag(cov))
t_stats  = coeffs / se
p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n - p))

# ── Results table ──────────────────────────────────────────────────────────────
def sig_stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    return ""

feature_names = ["intercept"] + FEATURES
results = pd.DataFrame({
    "feature":    feature_names,
    "coef":       coeffs,
    "std_err":    se,
    "t_stat":     t_stats,
    "p_value":    p_values,
    "sig":        [sig_stars(p) for p in p_values],
})

print(f"OLS Linear Regression — EU Voter Turnout")
print(f"{'─' * 60}")
print(f"  N        : {n}")
print(f"  R²       : {r2:.4f}")
print(f"  RMSE     : {rmse:.4f}")
print(f"{'─' * 60}")
print(results.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print()
print("Significance: * p<0.05  ** p<0.01  *** p<0.001")
print("Note: coefficients are on standardised features.")

# ── Actual vs predicted ────────────────────────────────────────────────────────
df["predicted"]  = y_pred
df["residual"]   = y - y_pred
print(f"\nResiduals — min: {df['residual'].min():.2f}  max: {df['residual'].max():.2f}")