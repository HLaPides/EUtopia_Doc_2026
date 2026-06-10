import pandas as pd
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# load data
df = pd.read_csv('../api/backend/ml_models/eurobarometer_cleaned.csv')

# drop nulls
df['left_right'] = df['left_right'].replace({97: float('nan'), 98: float('nan')})
df = df.dropna()

# features and target
X = df.drop(columns=['country', 'trust_eu', 'age', 'gender', 'political_interest'])
y = df['trust_eu']

print(f"Dataset size: {len(df)} rows")
print(f"Trust EU distribution:\n{y.value_counts()}")

# split data 80% train 20% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# train model
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# evaluate
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"\nTraining Accuracy: {train_score:.3f}")
print(f"Testing Accuracy:  {test_score:.3f}")
#print(f"\ncoef_vals: {json.dumps(model.coef_[0].tolist())}")
#print(f"intercept: {model.intercept_[0]}")


import matplotlib
matplotlib.use('Agg')  # prevents blocking popup windows
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 1. MULTICOLLINEARITY — correlation heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(X.corr(), annot=True, cmap='coolwarm', center=0)
plt.title('Feature Correlation Matrix')
plt.tight_layout()
plt.savefig('correlation_matrix.png')
plt.close()

# 2. OUTLIERS — boxplot
X.boxplot(figsize=(10, 6))
plt.title('Feature Distributions (Outlier Check)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('boxplot.png')
plt.close()

# 3. SAMPLE SIZE CHECK
print(f"\nSample size: {len(X)}")
print(f"Features: {X.shape[1]}")
print(f"Samples per feature: {len(X) / X.shape[1]:.0f}")
print(f"Minimum recommended: {X.shape[1] * 10}")