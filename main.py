import time
import requests
from environs import Env
from telegram import Bot


DVMN_REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'
DVMN_LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'


def form_notifications(attempts):
    notification_texts = []
    for attempt in attempts:
        notification_text = f"""У вас проверили работу:
["{attempt["lesson_title"]}"]({attempt["lesson_url"]})"""

        if attempt['is_negative']:
            notification_text += '\nК сожалению, в работе нашлись ошибки.'
        else:
            notification_text += '\nПреподавателю все понравилось, можно приступать к следующему уроку!'

        notification_texts.append(notification_text)
    return notification_texts


def start_polling():
    headers = {
        'Authorization': f'Token {env.str("DVMN_PERSONAL_TOKEN")}'
    }
    payload = {'timestamp': None}

    bot = Bot(token=env.str('TELEGRAM_BOT_TOKEN'))

    chat_id = env.str('TELEGRAM_USER_ID')

    while True:
        try:
            response = requests.get(
                DVMN_LONG_POLLING_URL,
                headers=headers,
                params=payload,
                timeout=95
            )
            response.raise_for_status()

            review_response = response.json()

            if review_response['status'] == 'found':
                notifications = form_notifications(
                    review_response['new_attempts']
                )
                for notification in notifications:
                    bot.send_message(
                        text=notification,
                        chat_id=chat_id,
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
            continue

        except requests.exceptions.ConnectionError:
            print('Отсутствует связь с сервисом, попробую еще через 5 сек...')
            time.sleep(5)
        except KeyboardInterrupt:
            print('\nРабота программы завершена')
            break


if __name__ == '__main__':
    env = Env()
    env.read_env()
    start_polling()
