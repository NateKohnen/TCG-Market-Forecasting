import pandas as pd
import matplotlib.pyplot as plt
from labellines import labelLines

df = pd.read_json("C:\\Users\\Nate\\PycharmProjects\\MarketPredictor\\tests"
                  "\\weekly-info\\SV_Weekly_Historical_Data_Above_20.json")
df['week'] = pd.to_datetime(df['week'])

specific_ids = [
    "sv6-214",
    "sv3pt5-199",
    "sv4pt5-234",
    "sv9-184",
    "sv3-223",
    "sv4pt5-232"
]
filtered = df[df['card_id'].isin(specific_ids)]

filtered.plot(x='week', y='week_avg', kind='line', figsize=(10, 6), label='card_id')

labelLines(plt.gca().get_lines(), zorder=2.5)
plt.title('Price Over Time')
plt.xlabel('week')
plt.ylabel('week_avg')
plt.grid(True)
plt.show()
