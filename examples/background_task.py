from twitch import UserAPI, App
from twitch.ext import tasks
import asyncio

counter = 0

@tasks.loop(seconds=10)
async def my_task(user: UserAPI):
    global counter
    counter += 1
    await user.send_chat_message(f'Check #{counter}')

async def main():
    async with App('CLIENT_ID', 'CLIENT_SECRET') as app:
        user = await app.add_user('USER_ID', 'ACCESS_TOKEN')
        await my_task.start(user)

asyncio.run(main())