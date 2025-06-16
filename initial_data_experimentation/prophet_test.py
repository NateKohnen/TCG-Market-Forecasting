import json
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Read from JSON
with open("mock_card_data.json", "r") as f:
    sales_data = json.load(f)

# Convert to DataFrame
rows = []
for card, sales in sales_data.items():
    for sale in sales:
        rows.append({
            "card": card,
            "ds": pd.to_datetime(sale["date"]),
            "y": sale["price"]
        })

df = pd.DataFrame(rows)
training_frame = df[~df['ds'].between("2026-11-30", "2027-01-01")]

def do_prophet_things():
    m = Prophet()
    m.fit(training_frame)
    future = m.make_future_dataframe(periods=31)
    forecast = m.predict(future)

    fig, ax = plt.subplots(figsize=(10, 6))
    m.plot(forecast, ax=ax)
    actual_frame = df[df['ds'] > training_frame['ds'].max()]
    ax.plot(actual_frame['ds'], actual_frame['y'], 'r.', label='Actual December Sales')
    plt.legend()
    plt.title("Forecast vs. Actuals (December)")
    plt.show()

do_prophet_things()
