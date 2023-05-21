from aiogram import Bot, Dispatcher, types, executor
import httpx
from environs import Env
import asyncio


DVMN_LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'


async def on_startup(dp):
    await poll_reviews()


async def form_notifications(attempts):
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


async def poll_reviews():
    headers = {
        'Authorization': f'Token {env.str("DVMN_PERSONAL_TOKEN")}'
    }
    payload = {'timestamp': None}

    chat_id = env.str('TELEGRAM_USER_ID')
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    DVMN_LONG_POLLING_URL,
                    headers=headers,
                    params=payload,
                    timeout=95
                )
            response.raise_for_status()

            review_response = response.json()

            if review_response['status'] == 'found':
                notifications = await form_notifications(
                    review_response['new_attempts']
                )
                for notification in notifications:
                    await bot.send_message(
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

        except httpx.TimeoutException:
            continue

        except httpx.ConnectError:
            print('Отсутствует связь с сервисом, попробую еще через 5 сек...')
            asyncio.sleep(5)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    bot = Bot(
        env.str('TELEGRAM_BOT_TOKEN'),
        parse_mode=types.ParseMode.MARKDOWN
    )

    dp = Dispatcher(bot)

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )
