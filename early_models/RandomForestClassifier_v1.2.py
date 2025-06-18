import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.exceptions import NotFittedError
import matplotlib.pyplot as plt

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
def backtest(data, model_fn, predictors, start=4, step=1, threshold=0.6):
    all_predictions = []

    # Expansions to be omitted
    undesirables = [
        "sv10",
        "sv9",
        "sv8pt5"
    ]

    # Cluster the dataframe according to card IDs, recording ID and all associated objects
    for card_id, group in data.groupby("card_id"):

        # Skips over members of specified expansions
        expansion = card_id.split("-")[0]
        # if expansion != "sv1":
        #     continue
        if expansion in undesirables:
            continue

        # Failsafe, sorts all card data chronologically
        print(f"Backtesting {card_id}...")
        group = group.sort_values("week").reset_index(drop=True)

        # Iterate through the data from the specified starting
        # point, and at the specified step rate
        for i in range(start, len(group) - step, step):
            train = group.iloc[:i]
            test = group.iloc[i:i+step]

            # Skip over untrainable sections
            if train["target"].nunique() < 2:
                continue

            # Define and calibrate the model
            model = model_fn()
            model.fit(train[predictors], train["target"])

            # Attempt to predict the target probabilistically
            # Revert to a binary prediction on error thrown
            try:
                probas = model.predict_proba(test[predictors])
                if probas.shape[1] == 2:
                    preds = (probas[:, 1] >= threshold).astype(int)
                else:
                    preds = model.predict(test[predictors])
            except NotFittedError:
                continue

            # Log the card ID, timestamp, and actual value alongside the prediction
            result = test[["card_id", "week", "target"]].copy()
            result["predictions"] = preds
            result["probability"] = probas[:, 1] if probas.shape[1] == 2 else 0.5
            all_predictions.append(result)

    # Coalesce all results into a single DataFrame
    return pd.concat(all_predictions, ignore_index=True)

# Thresholds to be tested against false positives
thresholds = [0.4, 0.5, 0.6, 0.7, 0.8]
metrics = []

# Backtests against the listed threshold values
for t in thresholds:
    preds = backtest(df_clean, model_fn, feature_cols, threshold=t)
    print(f"\nEvaluation at threshold {t} completed.\n")

    # Determines various metrics for assessing model potency
    precision = precision_score(preds["target"], preds["predictions"])
    recall = recall_score(preds["target"], preds["predictions"])
    f1 = f1_score(preds["target"], preds["predictions"])
    metrics.append((t, precision, recall, f1))
print(f"************************")
print(f"\nALL EVALUATIONS COMPLETED.\n")
print(f"************************")

# I have absolutely no idea what this does, the funny wizard told me to put it here
thresholds, precision, recall, f1 = zip(*metrics)

# Visualizer, thank you wibzard
plt.figure(figsize=(10, 5))
plt.plot(thresholds, precision, label="Precision", marker="o")
plt.plot(thresholds, recall, label="Recall", marker="o")
plt.plot(thresholds, f1, label="F1 Score", marker="o")
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.title("Threshold Tuning for Predicting Price Increase")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
