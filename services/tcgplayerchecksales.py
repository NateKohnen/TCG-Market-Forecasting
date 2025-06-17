from datetime import datetime
from multiprocessing import Pool, cpu_count
import requests
import time
import re
import random


BLACKLIST_WORDS = ["japanese", "chinese", "korean", "psa", "cgc", "graded", "beckett", "china", "japan", "korea"]


USER_AGENTS = [
    # Windows - Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",

    # Windows - Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",

    # macOS - Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",

    # macOS - Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",

    # Linux - Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.92 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.91 Safari/537.36",

    # Android - Chrome
    "Mozilla/5.0 (Linux; Android 12; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",

    # iOS - Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
]


def get_price_history(card):
    """
    Generates a dictionary of weekly sale reports of a given card from the past year via scraping TCGplayer.

    args:
        card (Card):    Card to generate sales data on.

    returns:
        dictionary:     The dictionary containing important information on the sales of the given card.
    """
    product_id = get_tcgplayer_product_id_from_redirect(card.tcgplayer_link)
    url = f"https://infinite-api.tcgplayer.com/price/history/{product_id}/detailed?range=annual"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": f"https://www.tcgplayer.com/product/{product_id}",
        "Origin": "https://www.tcgplayer.com",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    cookies = {
        # These help simulate a legit browser session
        "tcg-uuid": "5fcec7f9-26b2-4c31-a4ca-29dcf63d9e50",
        # Other cookies if needed...
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    
    if not(response.status_code == 200):
        response.raise_for_status()
    json_file = response.json()
    price_history = json_file['result'][0]['buckets']
    grouped_data = {}

    for bucket in price_history:
        new_row = {}
        date = date_str = bucket["bucketStartDate"]
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        new_row['week'] = date
        new_row['num_sold'] = int(bucket['quantitySold'])
        new_row['min_price'] = float(bucket['lowSalePrice'])
        new_row['max_price'] = float(bucket['highSalePrice'])
        new_row['week_avg'] = float(bucket['marketPrice'])
        grouped_data.setdefault(card.card_id, []).append(new_row)

    return grouped_data


def get_tcgplayer_product_id_from_redirect(pokemon_tcg_url):
    """
    Gets TCGplayer's product id from a given url.

    args:
        pokemon_tcg_url (str):  The url for any given pokemon card.

    returns:
        str:    TCGplayer's product id for the given link.
    """
    try:
        response = requests.get(pokemon_tcg_url, allow_redirects=True)
        final_url = response.url
        match = re.search(r'/product/(\d+)', final_url)
        return match.group(1) if match else None
    except Exception as e:
        print("Error:", e)
        return None


def get_price_history_for_list_of_cards(cards):
    """
    Creates a dictionary of weekly sales for every card in a given list.

    args:
        cards (list):   list of Card objects to scrape TCGplayer prices for. 
    """
    new_list = []
    counter = 0
    for card in cards:
        time.sleep(random.uniform(1.5, 6.5))
        if counter % 15 == 0:
            time.sleep(10)
        new_list.append(get_price_history(card))
        counter = counter + 1
    
    return new_list