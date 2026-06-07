import pandas as pd
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# load data
df = pd.read_csv('../datasets/eurobarometer_cleaned.csv')

# drop nulls
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
print(f"\ncoef_vals: {json.dumps(model.coef_[0].tolist())}")
print(f"intercept: {model.intercept_[0]}")