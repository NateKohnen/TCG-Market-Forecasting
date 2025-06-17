import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score


"""
DEVELOPER CONSTANTS
"""

# Absolute path reference for scraped JSON data
# Super useful for everyone else
JSON_FILE_PATH = ("C:\\Users\\Nate\\PycharmProjects"
                  "\\MarketPredictor\\tests\\weekly-info"
                  "\\scarlet_violet_era_weekly_sales.json")

# JSON attribute references
PARAM_CID = "card_id"  # Card identifier
PARAM_WEEK = "week"  # Specific 7-day period (YYYY-MM-DD)
PARAM_VOL = "num_sold"  # Number of card sales made
PARAM_PMIN = "min_price"  # Minimum sell price instance
PARAM_PMAX = "max_price"  # Maximum sell price instance
PARAM_AVG = "week_avg"  # Average sell price over all instances

# Model-facing predictive attribute references
PARAM_NEXT = "next_avg"  # Next week's average sell price
PARAM_TARG = "target"  # Actual market directionality at instance (1 is +, 0 is -/=)

# Model-facing historical attribute references
PARAM_L1AVG = "lag1_avg"  # Prior (week[-1]) average
PARAM_L1VOL = "lag1_vol"  # Prior (week[-1]) volume

# Model-facing rolling attribute references
INT_R4 = 4  # Number of previous weeks present in rolling value, including current
PARAM_R4AVG = f"roll{INT_R4}_avg"  # Rolling average price over {INT_R4} weeks
PARAM_R4VOL = f"roll{INT_R4}_vol"  # Rolling average sales volume over {INT_R4} weeks

"""
DEVELOPER CONSTANTS
"""


# Translate JSON data to a pandas DataFrame
df = pd.read_json(JSON_FILE_PATH)

# Item sorting failsafe, quantize card IDs, and convert datetime
df = df.sort_values([PARAM_CID, PARAM_WEEK])
codes, uniques = pd.factorize(df[PARAM_CID])
df[PARAM_CID] = [c for c in codes]
df[PARAM_WEEK] = pd.to_datetime(df[PARAM_WEEK])

# Target (directionality)
df[PARAM_NEXT] = df.groupby(PARAM_CID)[PARAM_AVG].shift(-1)
df[PARAM_TARG] = (df[PARAM_NEXT] > df[PARAM_AVG]).astype(int)

# Lag features
df[PARAM_L1AVG] = df.groupby(PARAM_CID)[PARAM_AVG].shift(1)
df[PARAM_L1VOL] = df.groupby(PARAM_CID)[PARAM_VOL].shift(1)

# Rolling averages
df[PARAM_R4AVG] = (
    df.groupby(PARAM_CID)[PARAM_AVG]
      .rolling(window=INT_R4)
      .mean()
      .reset_index(0, drop=True)
)
df[PARAM_R4VOL] = (
    df.groupby(PARAM_CID)[PARAM_VOL]
      .rolling(window=INT_R4)
      .sum()
      .reset_index(0, drop=True)
)

# Constructs the model
model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

# Defines which attributes will be model-facing
predictors = [PARAM_CID, PARAM_AVG, PARAM_L1AVG, PARAM_R4AVG, PARAM_L1VOL, PARAM_R4VOL]

# Hyper-simple separation of training and testing data
train = df[df[PARAM_WEEK] < "2025-04-01"]
test = df[df[PARAM_WEEK] >= "2025-04-01"]

# Calibrate the model on the training data
model.fit(train[predictors], train[PARAM_TARG])

# Produce a forecast for the test data
forecast = model.predict(test[predictors])
forecast = pd.Series(forecast, index=test.index)

# Evaluate forecast precision
score = precision_score(test[PARAM_TARG], forecast)
print(score)
