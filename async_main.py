from aiogram import Bot, Dispatcher, types, executor
import httpx
from environs import Env
import asyncio


DVMN_LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'


async def on_startup(dp):
    await poll_reviews()


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
                    params=payload, timeout=95
                )
            response.raise_for_status()

            review_response = response.json()

            if review_response['status'] == 'found':
                for attempt in review_response['new_attempts']:
                    if attempt['is_negative']:
                        await bot.send_message(
                            text=f'У вас проверили работу:\n'
                                 f'["{attempt["lesson_title"]}"]({attempt["lesson_url"]})\n'
                                 f'К сожалению, в работе нашлись ошибки.',
                            chat_id=chat_id
                            )
                    else:
                        await bot.send_message(
                            text=f'У вас проверили работу:\n'
                                 f'["{attempt["lesson_title"]}"]({attempt["lesson_url"]})\n'
                                 f'Преподавателю все понравилось, можно приступать к следующему уроку!',
                            chat_id=chat_id
                            )
                payload = {
                    'timestamp': review_response['last_attempt_timestamp']
                }
            else:
                payload = {
                    'timestamp': review_response['timestamp_to_request']
                }
                print(review_response)

        except httpx.TimeoutException:
            print('Сервис не ответил, пробую еще...')

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
