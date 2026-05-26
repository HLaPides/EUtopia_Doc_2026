# IMPORT LIBRARIES AND LOAD DATA

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score
import pickle
import os

# load data
df = pd.read_csv('../datasets/eu_turnout.csv')
national = pd.read_excel('../datasets/national_turnout.xlsx')
national = national.iloc[:, [1, 3, 4]]

#-----

# CLEAN DATA

# fix year — extract just the year number
national['year'] = pd.to_datetime(national['year']).dt.year

# fix turnout — remove % sign and convert to float
national['Voter Turnout'] = national['Voter Turnout'].str.replace('%', '').astype(float)

# rename columns to match main df
national = national.rename(columns={
    'ISO2': 'country',
    'Voter Turnout': 'national_turnout'
})

df['year'] = df['year'].astype(int)
national['year'] = national['year'].astype(int)

# sort both before merging
df = df.sort_values('year').reset_index(drop=True)
national = national.sort_values('year').reset_index(drop=True)

# merge — matches each EP election to closest national election before it
df = pd.merge_asof(
    df,
    national[['country', 'year', 'national_turnout']],
    on='year',
    by='country',
    direction='backward'
)

print(df[['country', 'year', 'national_turnout']].head(20))
print(df['national_turnout'].isnull().sum())

df = df.fillna(df.mean(numeric_only=True))


#---------

# MODEL

# drops non-feature columns in X
X = df.drop(columns=['country', 'year', 'voter_turnout'])
y = df['voter_turnout']

print(national.columns.tolist())
print(national.head())


# train model
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=2,
    min_samples_leaf=10,
    min_samples_split=10,
    random_state=1
)
model.fit(X, y)

# evaluate model
scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"R² score: {scores.mean():.3f} (+/- {scores.std():.3f})")
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_score
mae_scores = cross_val_score(model, X, y, cv=3, scoring='neg_mean_absolute_error')
print(f"Average error: {-mae_scores.mean():.1f} %")

#-----

# CHECK AND SAVE

# to see whether it's overfitting
'''train_score = model.score(X, y)
cv3 = cross_val_score(model, X, y, cv=3, scoring='r2').mean()
print(f"Training R²: {train_score:.3f}")
print(f"CV=3 R²:     {cv3:.3f}")'''

# find correlation strength of each feature
# print(df.corr(numeric_only=True)['voter_turnout'].sort_values(ascending=False))

# save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)


#print("model.pkl saved to ml-src/")'''