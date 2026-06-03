"""
This file creates plots that allows you to analyze the model for linearity, homoscedasticity, and autocorrelation
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("../datasets/eu_turnout_clean.csv")

FEATURES = [
    "gdp_per_capita", "unemployment_rate", "compulsory_voting",
    "years_eu_membership", "urbanization_rate", "median_age",
    "eu_net_beneficiary", "weekend_voting", "national_turnout",
]

X = df[FEATURES].values
y = df["voter_turnout"].values
X_scaled = (X - X.mean(axis=0)) / X.std(axis=0)
X_int = np.column_stack([np.ones(len(X_scaled)), X_scaled])
coeffs, _, _, _ = np.linalg.lstsq(X_int, y, rcond=None)
y_pred = X_int @ coeffs
resids = y - y_pred

compulsory = df["compulsory_voting"].values == 1

fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# residual vs fitted, checks for linearity and homoscedasticity.
# compulsory voting marked in red, countries at the end are Belgium and Luxembourg who both consistently enforce their compulsory voting unlike Greece
axes[0].scatter(y_pred[~compulsory], resids[~compulsory], alpha=0.5, s=20, label="voluntary")
axes[0].scatter(y_pred[compulsory],  resids[compulsory],  alpha=0.5, s=20, label="compulsory", color="red")
axes[0].axhline(0, color="black", linewidth=1, linestyle="--")
axes[0].set_xlabel("Fitted values")
axes[0].set_ylabel("Residuals")
axes[0].set_title("Residuals vs Fitted")
axes[0].legend(fontsize=8)

# residuals vs order checks autocorrelation
axes[1].plot(resids, alpha=0.6, linewidth=0.8)
axes[1].axhline(0, color="red", linewidth=1, linestyle="--")
axes[1].set_xlabel("Observation index")
axes[1].set_ylabel("Residuals")
axes[1].set_title("Residuals vs Order")

plt.tight_layout()
plt.show()