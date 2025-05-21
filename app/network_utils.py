# Place this retry helper at the bottom of your routes.py
import requests
import time
import logging


def fetch_tmdb_with_retry(url, params=None, retries=4, delay=0.5):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"TMDB returned {response.status_code}:{response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt+1} failed: {e}")
    return None
