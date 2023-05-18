import time
import requests
from environs import Env
from telegram import Bot


DVMN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'


env = Env()
env.read_env()

DVMN_PERSONAL_TOKEN = env.str('DVMN_PERSONAL_TOKEN')

TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

TELEGRAM_USER_ID = env.str('TELEGRAM_USER_ID')

headers = {
    'Authorization': f'Token {DVMN_PERSONAL_TOKEN}'
}


def start_polling():
    payload = {'timestamp': None}
    while True:
        try:
            response = requests.get(
                DVMN_LONG_POLLING_URL,
                headers=headers,
                params=payload
            )
            response.raise_for_status()

            review_response = response.json()

            if review_response['status'] == 'found':
                for attempt in review_response['new_attempts']:
                    if attempt['is_negative']:
                        bot.send_message(
                            text=f'У вас проверили работу:\n'
                                 f'["{attempt["lesson_title"]}"]({attempt["lesson_url"]})\n'
                                 f'К сожалению, в работе нашлись ошибки.',
                            chat_id=TELEGRAM_USER_ID,
                            parse_mode='Markdown'
                            )
                    else:
                        bot.send_message(
                            text=f'У вас проверили работу:\n'
                                 f'["{attempt["lesson_title"]}"]({attempt["lesson_url"]})\n'
                                 f'Преподавателю все понравилось, можно приступать к следующему уроку!',
                            chat_id=TELEGRAM_USER_ID,
                            parse_mode='Markdown'
                            )
                payload = {
                    'timestamp': review_response['last_attempt_timestamp']
                }
            else:
                payload = {
                    'timestamp': review_response['timestamp_to_request']
                }

        except requests.exceptions.ReadTimeout:
            print('Сервис не ответил, пробую еще...')

        except requests.exceptions.ConnectionError:
            print('Отсутствует связь с сервисом, попробую еще через 5 сек...')
            time.sleep(5)
        except KeyboardInterrupt:
            print('\nРабота программы завершена')
            break


if __name__ == '__main__':
    start_polling()
