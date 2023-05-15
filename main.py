import requests
from environs import Env
from pprint import pprint


DVMN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'

env=Env()
env.read_env()

DVMN_PERSONAL_TOKEN = env.str('DVMN_PERSONAL_TOKEN')

headers= {
    'Authorization': f'Token {DVMN_PERSONAL_TOKEN}'
}

response = requests.get(DVMN_REVIEWS_URL, headers=headers)
response.raise_for_status()

review_response = response.json()

pprint(review_response)
