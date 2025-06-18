import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

#<editor-fold desc="Developer constants">
"""
DEVELOPER CONSTANTS
"""

# Absolute path reference for scraped JSON data
# Super useful for everyone else I know, you're welcome
SV_ABOVE_20_PATH = ("C:\\Users\\Nate\\PycharmProjects\\MarketPredictor"
                    "\\tests\\weekly-info\\SV_Weekly_Historical_Data_Above_20.json")
ALL_SV_PATH = ("C:\\Users\\Nate\\PycharmProjects\\MarketPredictor"
               "\\tests\\weekly-info\\scarlet_violet_era_weekly_sales.json")

"""
DEVELOPER CONSTANTS
"""
#</editor-fold>

#<editor-fold desc="Data loading & preprocessing">
# Translate JSON data to a pandas DataFrame and converts datetime appropriately
df = pd.read_json(SV_ABOVE_20_PATH)
df = df.sort_values(["card_id", "week"]).reset_index(drop=True)
df["week"] = pd.to_datetime(df["week"])

# Directionality (target) attribute, i.e. trend + (1) or - (0)
df["next_avg"] = df.groupby("card_id")["week_avg"].shift(-1)
df["target"] = (df["next_avg"] > df["week_avg"]).astype(int)

# Lagging reference attributes
df["lag1_avg"] = df.groupby("card_id")["week_avg"].shift(1)
df["lag2_avg"] = df.groupby("card_id")["week_avg"].shift(2)
df["lag1_vol"] = df.groupby("card_id")["num_sold"].shift(1)
df["lag2_vol"] = df.groupby("card_id")["num_sold"].shift(2)

rollers = []

# Rolling average sales price
horizons = [2, 4, 8, 16]
for horizon in horizons:
    rolling_avg = (
        df.groupby("card_id")["week_avg"]
          .rolling(window=horizon)
          .mean()
          .reset_index(0, drop=True)
    )

    col_name = f"week_vs_roll{horizon}_avg"
    df[col_name] = df["week_avg"] / rolling_avg
    rollers.append(col_name)

# Rolling average sales volume
horizonts = [2, 4]
for horizon in horizonts:
    rolling_vol = (
        df.groupby("card_id")["num_sold"]
        .rolling(window=horizon)
        .mean()
        .reset_index(0, drop=True)
    )

    col_name = f"week_vs_roll{horizon}_vol"
    df[col_name] = df["num_sold"] / rolling_vol
    rollers.append(col_name)

# Rolling directionality trend
horizaints = [2, 3, 4, 8, 16]
for horizon in horizaints:
    trend = (
        df.groupby("card_id")["target"]
        .rolling(window=horizon)
        .sum()
        .reset_index(0, drop=True)
    )

    col_name = f"trend{horizon}"
    df[f"trend{horizon}"] = trend / horizon
    rollers.append(col_name)

# Removes any null values from preprocessing
df_clean = df.dropna()
#</editor-fold>

# Clarifies training attributes and prediction objectives
feature_cols = [
    "week_avg", "num_sold",
    "lag1_avg", "lag2_avg",
    "lag1_vol", "lag2_vol"
] + rollers

# Constructs a model
def model_fn():
    return RandomForestClassifier(n_estimators=100, random_state=42)

# Backtests the model, mimicking more data being added over time
def backtest(data, model_fn, predictors, start=4, step=1):
    all_predictions = []
    undesirables = [
        "sv10",
        "sv9",
        "sv8pt5"
    ]

    for card_id, group in data.groupby("card_id"):
        expansion = card_id.split("-")[0]
        # if expansion != "sv1":
        #     continue
        if expansion in undesirables:
            continue

        print(f"Backtesting {card_id}...")
        group = group.sort_values("week").reset_index(drop=True)

        for i in range(start, len(group) - step, step):
            train = group.iloc[:i]
            test = group.iloc[i:i+step]

            model = model_fn()
            model.fit(train[predictors], train["target"])

            preds = model.predict(test[predictors])
            result = test[["card_id", "week", "target"]].copy()
            result["prediction"] = preds
            all_predictions.append(result)

    return pd.concat(all_predictions, ignore_index=True)

# Obtains backtested predictions
bt_preds = backtest(df_clean, model_fn, feature_cols)
print(f"Evaluation COMPLETE.")

# Card-specific accuracies
bt_preds["correct"] = (bt_preds["target"] == bt_preds["prediction"]).astype(int)
card_acc = bt_preds.groupby("card_id")["correct"].mean().sort_values(ascending=False)
print("Top 10 Cards by Accuracy:")
print(card_acc.head(10).to_string())

# Plot of weekly accuracies
weekly_acc = bt_preds.groupby("week")["correct"].mean()
plt.figure(figsize=(10, 4))
weekly_acc.plot(marker="o")
plt.title("Weekly Prediction Accuracy")
plt.xlabel("Week")
plt.ylabel("Accuracy")
plt.grid(True)
plt.tight_layout()
plt.show()

# Visualization of confusion values
confusion = confusion_matrix(bt_preds["target"], bt_preds["prediction"])
plt.figure(figsize=(4, 4))
sns.heatmap(confusion, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Predicted ↓/=", "Predicted ↑"],
            yticklabels=["Actual ↓/=", "Actual ↑"])
plt.title("Confusion Matrix")
plt.xlabel("Prediction")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

gross_accuracy = accuracy_score(bt_preds["target"], bt_preds["prediction"])
print(f"Overall accuracy score: {gross_accuracy}")
