import requests
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
while True:
    try:
        response = requests.get(
            DVMN_LONG_POLLING_URL,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()

        review_response = response.json()

        pprint(review_response)
    except requests.exceptions.ReadTimeout:
        print('Сервис не ответил, пробую еще...')
        continue

