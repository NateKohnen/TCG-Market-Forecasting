import concurrent.futures
import time
import random
import requests
from services import tcgplayerchecksales
MAX_RETRIES = 3
BASE_SLEEP = 10  # seconds, will increase with each retry

def process_card(card):
    """
    Introduces failsafes for scraping TCGplayer  using tcgplayer.checksales.get_price_history() function.

    args:
        card (Card):    The card to scrape data for. 
    
    returns:
        dictionary: Containing all the weekly sale reports for the given card.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            history = tcgplayerchecksales.get_price_history(card)
            return history
        
        except requests.exceptions.HTTPError as e:
            # Handle specific 403
            if e.response.status_code == 403:
                print(f"[403] Blocked while processing {card.card_id}, retrying attempt {attempt}/{MAX_RETRIES}...")
                # sleep_time = BASE_SLEEP * attempt + random.uniform(1, 5)
                # time.sleep(sleep_time)
            else:
                print(f"[HTTP ERROR] {card.card_id}: {e}")
                break  # for non-403 errors, don't retry

        except Exception as e:
            print(f"[ERROR] {card.card_id}: {e}")
            break  # break on unexpected errors
    return {"failed": card} # if all retries fail
