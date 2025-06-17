import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
import matplotlib.pyplot as plt


"""
DEVELOPER CONSTANTS
"""

# Absolute path reference for scraped JSON data
# Super useful for everyone else
JSON_FILE_PATH = ("C:\\Users\\Nate\\PycharmProjects"
                  "\\MarketPredictor\\tests\\weekly-info"
                  "\\SV_Weekly_Historical_Data_Above_20.json")

# JSON attribute references
JPARAM_CID = "card_id"  # Card identifier
JPARAM_WEEK = "week"  # Specific 7-day period (YYYY-MM-DD)
JPARAM_VOL = "num_sold"  # Number of card sales made
JPARAM_PMIN = "min_price"  # Minimum sell price instance
JPARAM_PMAX = "max_price"  # Maximum sell price instance
JPARAM_AVG = "week_avg"  # Average sell price over all instances

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
df = df.sort_values([JPARAM_CID, JPARAM_WEEK])
codes, uniques = pd.factorize(df[JPARAM_CID])
df[JPARAM_CID] = [c for c in codes]
df[JPARAM_WEEK] = pd.to_datetime(df[JPARAM_WEEK])

# Target (directionality)
df[PARAM_NEXT] = df.groupby(JPARAM_CID)[JPARAM_AVG].shift(-1)
df[PARAM_TARG] = (df[PARAM_NEXT] > df[JPARAM_AVG]).astype(int)
print(df[PARAM_NEXT].isna().sum())
quit()

# Lag features
df[PARAM_L1AVG] = df.groupby(JPARAM_CID)[JPARAM_AVG].shift(1)
df[PARAM_L1VOL] = df.groupby(JPARAM_CID)[JPARAM_VOL].shift(1)

# Rolling averages
df[PARAM_R4AVG] = (
    df.groupby(JPARAM_CID)[JPARAM_AVG]
      .rolling(window=INT_R4)
      .mean()
      .reset_index(0, drop=True)
)
df[PARAM_R4VOL] = (
    df.groupby(JPARAM_CID)[JPARAM_VOL]
      .rolling(window=INT_R4)
      .sum()
      .reset_index(0, drop=True)
)

# Constructs the model
model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

# Defines which attributes will be model-facing
predictors = [JPARAM_CID, JPARAM_AVG, PARAM_L1AVG, PARAM_R4AVG, PARAM_L1VOL, PARAM_R4VOL]

# Hyper-simple separation of training and testing data
train = df[df[JPARAM_WEEK] < "2025-04-01"]
test = df[df[JPARAM_WEEK] >= "2025-04-01"]

# Calibrate the model on the training data
model.fit(train[predictors], train[PARAM_TARG])

# Produce a forecast for the test data
forecast = model.predict(test[predictors])
forecast = pd.Series(forecast, index=test.index)

# Evaluate forecast precision
score = precision_score(test[PARAM_TARG], forecast)
combined = pd.concat([test[PARAM_TARG], forecast], axis=1)

# Format labeling
combined.columns = ["actual", "predicted"]
combined = combined.assign(week=test[JPARAM_WEEK])
combined = combined.sort_values(JPARAM_WEEK)

# Display visual
ax = combined.plot(
    x="week",
    y=["actual", "predicted"],
    figsize=(12, 5),
    style={"actual": "b-", "predicted": "r--"},
    title="True vs. Predicted Direction Over Time"
)
ax.set_ylabel("Direction (0 = down/same, 1 = up)")
plt.show()
