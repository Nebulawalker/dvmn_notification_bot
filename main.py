import time
import requests
import time
from environs import Env
from pprint import pprint


DVMN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'

env=Env()
env.read_env()

DVMN_PERSONAL_TOKEN = env.str('DVMN_PERSONAL_TOKEN')

headers= {
    'Authorization': f'Token {DVMN_PERSONAL_TOKEN}'
}
start_time = time.monotonic()
response = requests.get(DVMN_LONG_POLLING_URL, headers=headers)
response.raise_for_status()

review_response = response.json()

pprint(review_response)
print(f'Таймаут = {time.monotonic() - start_time}') #90 sec

