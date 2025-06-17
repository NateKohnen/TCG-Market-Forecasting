import mysql.connector
import json
from operator import itemgetter

def get_historical_tcg_daily_data(card, connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT sale_date AS date, sale_price as price FROM tcgplayer_sales WHERE card_id = %s;", (card.card_id,))
    rows = cursor.fetchall()

    grouped_data = {}
    for row in rows:
        if row['price'] is not None:
            row['price'] = float(row['price'])
        grouped_data.setdefault(card.card_id, []).append(row)
    
    json_data = json.dumps(grouped_data, indent=2, default=str)

    with open(f'{card.card_id}_sales.json', 'w') as f:
        f.write(json_data)

    cursor.close()
    connection.close()

def get_all_historical_daily_tcg_data(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT card_id, sale_date AS date, sale_price as price FROM tcgplayer_sales;")
    rows = cursor.fetchall()

    grouped_data = {}

    for row in rows:
        card_id = row.pop('card_id')
        if row['price'] is not None:
            row['price'] = float(row['price'])
        grouped_data.setdefault(card_id, []).append(row)
    for card_id in grouped_data:
        grouped_data[card_id].sort(key=itemgetter('date'))

    with open('tcgplayer_sales_grouped.json', 'w') as f:
        json.dump(grouped_data, f, indent=2, default=str)
    
    cursor.close()
    connection.close()

def get_historical_tcg_monthly_data(card, connection):
    """
    Writes a JSON file for a given card object.

    args:
    card (Card):                    A card object to generate a JSOn file of sales.
    connection (SQL.connection):    Connection to SQL database.
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT week_of, quantity_sold, low_sale_price, high_sale_price, market_price FROM tcgplayer_weekly_sales WHERE card_id = %s;", (card.card_id,))
    rows = cursor.fetchall()
    grouped_data = {}
    for row  in rows:
        grouped_data.setdefault(card.card_id, []).append(row)
    
    json_data = json.dumps(grouped_data, indent=2, default=str)

    with open(f'{card.card_id}_sales.json', 'w') as f:
        f.write(json_data)

    cursor.close()
    connection.close()

def get_all_historical_tcg_monthly_data(connection, file_output_name='tcgplayer_weekly_sales_grouped'):
    """
    Generates a json file of all available TCGplayer weekly sales within the given connection.

    args:
        connection (SQL.connection):    Connection to SQL database.
        file_output_name (str):         The name of the output file (EXCLUDING .JSON) Defaults to 'tcgplayer_weekly_sales_grouped'
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT s.card_id, s.week, s.num_sold, s.min_price, s.max_price, s.week_avg FROM tcgplayer_weekly_sales s JOIN (SELECT DISTINCT(card_id) FROM tcgplayer_weekly_sales WHERE week_avg >= 20) AS filtered_cards ON s.card_id = filtered_cards.card_id;")
    rows = cursor.fetchall()


    rows.sort(key=itemgetter('card_id', 'week'))

    # Dump directly, now that card_id is included in each row
    with open(file_output_name + ".json", 'w') as f:
        json.dump(rows, f, indent=2, default=str)
    
    cursor.close()
    connection.close()
