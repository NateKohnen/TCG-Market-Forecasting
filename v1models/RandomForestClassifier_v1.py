import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

#<editor-fold desc="Developer Constants">
"""
DEVELOPER CONSTANTS
"""

# Absolute path reference for scraped JSON data
# Super useful for everyone else I know, you're welcome
JSON_FILE_PATH = ("C:\\Users\\Nate\\PycharmProjects"
                  "\\MarketPredictor\\tests\\weekly-info"
                  "\\SV_Weekly_Historical_Data_Above_20.json")

"""
DEVELOPER CONSTANTS
"""
#</editor-fold>

# Translate JSON data to a pandas DataFrame and converts datetime appropriately
df = pd.read_json(JSON_FILE_PATH)
df["week"] = pd.to_datetime(df["week"])

# Directionality (target) attribute, i.e. trend + (1) or - (0)
df["next_avg"] = df.groupby("card_id")["week_avg"].shift(-1)
df["target"] = (df["next_avg"] > df["week_avg"]).astype(int)

# Lagging reference attributes
df["lag1_avg"] = df.groupby("card_id")["week_avg"].shift(1)
df["lag1_vol"] = df.groupby("card_id")["num_sold"].shift(1)

# Rolling 4-week average sale price
df["roll4_avg"] = (
    df.groupby("card_id")["week_avg"]
      .rolling(window=4)
      .mean()
      .reset_index(0, drop=True)
)
df["roll4_vol"] = (
    df.groupby("card_id")["num_sold"]
      .rolling(window=4)
      .sum()
      .reset_index(0, drop=True)
)

# Removes any null values from preprocessing
df_clean = df.dropna(subset=["target"])

# Clarifies training attributes and prediction objectives
feature_cols = [
    "week_avg", "num_sold",
    "lag1_avg", "lag1_vol",
    "roll4_avg", "roll4_vol"
]
X = df_clean[feature_cols]
y = df_clean["target"]

# Split training and testing data by cutoff
cutoff = pd.to_datetime("2025-04-01")
train = df_clean[df_clean["week"] < cutoff]
test = df_clean[df_clean["week"] >= cutoff]

# Assign dependent and independent train/test datasets
X_train = train[feature_cols]
y_train = train["target"]
X_test = test[feature_cols]
y_test = test["target"]

# Constructs the model
model = RandomForestClassifier(n_estimators=100, random_state=1)
model.fit(X_train, y_train)
forecast = model.predict(X_test)

print(f"Accuracy: {accuracy_score(y_test, forecast)}\n"
      f"Confusion Matrix: {confusion_matrix(y_test, forecast)}")
