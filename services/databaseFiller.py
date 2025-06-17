from pokemontcgsdk import RestClient
from pokemontcgsdk import Set
from pokemontcgsdk import Card
import mysql.connector

RestClient.configure('3739caae-bf99-42f7-a473-50b7d67669d1')

def add_sets_to_db(connection):
    """
    Takes all the sets from the PokemonTCGSDK Set object and inserts them into the given connection.

    Args:
        connection (SQL.Connection): The connection to SQL database.    
    """
    query = """
        INSERT INTO sets (set_id, set_name, series, release_date, symbol, logo, total_cards)
        VALUES (%s, %s, %s, %s, %s, %s, %s);"""
    
    for set in Set.all():
        try:
                with connection.cursor() as cursor:
                    cursor.execute(query, (set.id, set.name, set.series, set.releaseDate, set.images.symbol, set.images.logo, set.total))
                    connection.commit()  # Commit the transaction to save the changes
                    cursor.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cursor.close()
    print("done")


def add_cards_from_set(connection, set_id):
    """
    Takes a given set id and adds the cards from that given set from the PokemonTCGSDK.

    args:
        connection (SQL.Connection):    The connection to SQL database.
        set_id (str):                   The given set_id to add all cards from.
    """
    cards = Card.where(q=f'set.id:{set_id}')
    for card in cards:
        query = """
        INSERT INTO cards (card_id, name, set_id, rarity, number, small_image, big_image, supertype)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (card.id, card.name, card.set.id, card.rarity, card.number, card.images.small, card.images.large, card.supertype))
                connection.commit()  # Commit the transaction to save the changes
                cursor.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cursor.close()
    print("done")

def add_weekly_tcg_sales_to_db(connection, sales):
    """
    Takes a dictionary sales and pushes said information to SQL connection.

    args:
        connection (SQL.Connection):    The connection to SQL datbase.
        sales (dict):                   A dictionary of sales sales.
    """
    card_id = list(sales.keys())[0]
    query = """
            Insert INTO tcgplayer_weekly_sales (card_id, week, num_sold, min_price, max_price, week_avg)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
    for sale in sales[card_id]:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (card_id, sale["week"], sale["num_sold"], sale["min_price"], sale["max_price"], sale["week_avg"]))
                connection.commit()
                cursor.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cursor.close()