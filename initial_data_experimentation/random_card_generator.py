import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import json

SAMPLE_SIZE = 1
TIMEFRAME = 30
START_DATE = "2025-01-01"
SEED = None
PRICE_RANGE = round(np.random.uniform(100.00, 250.00), 2)
AVG_TRADES = np.random.uniform(1, 3)

def generate_mock_card_data(n_cards=SAMPLE_SIZE, n_days=TIMEFRAME, start_date=START_DATE, seed=SEED):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    def simulate_price_series(base_price, volatility, trend_smoothness, shock_chance):
        price = base_price
        series = []
        momentum = 0
        for _ in range(n_days):
            if np.random.rand() < shock_chance:
                momentum += np.random.normal(0, base_price * 0.5)
            drift = np.random.normal(0, trend_smoothness)
            momentum = momentum * 0.95 + drift
            price += momentum + np.random.normal(0, volatility)
            price = max(0.25, round(price, 2))
            series.append(price)
        return series

    def generate_trade_history(name, price_series, trade_rate, base_date):
        for day_index, price in enumerate(price_series):
            n_trades = np.random.poisson(lam=trade_rate)
            trade_date = (base_date + timedelta(days=day_index)).strftime("%Y-%m-%d")
            for _ in range(n_trades):
                price_noise = np.random.normal(0, price * 0.02)  # 2% random variance
                noisy_price = max(0.25, round(price + price_noise, 2))
                sales.append({"name": name, "date": trade_date, "price": noisy_price})

    base_date = pd.to_datetime(start_date)
    sales = []

    for i in range(n_cards):
        name = f"Card {i+1}"
        price_range = PRICE_RANGE
        avg_trades = AVG_TRADES
        volatility = 0
        # volatility = np.random.uniform(0.2, price_range * 0.05)
        trend_smoothness = np.random.uniform(0, 0.3)
        shock_chance = 0
        # shock_chance = np.random.uniform(0.005, 0.02)

        price_series = simulate_price_series(price_range, volatility, trend_smoothness, shock_chance)
        generate_trade_history(name, price_series, avg_trades, base_date)

    return sales

# Generate and preview
mock_data = generate_mock_card_data()

# Write to JSON
with open("mock_card_data.json", "w") as f:
    json.dump(mock_data, f, indent=2)
