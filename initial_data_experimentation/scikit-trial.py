import pandas as pd

JSON_FILE_PATH = "mock_card_data.json"

# Translate JSON data to a pandas DataFrame
df = pd.read_json(JSON_FILE_PATH)
print(df)
