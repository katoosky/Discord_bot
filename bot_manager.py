import asyncio
from threading import Thread

import bot1
import bot2

loop = asyncio.get_event_loop()
# botくん1号の起動
job = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot1.bot.start(bot1.token, Bot=True), loop))
job.start()

# botくん2号の起動
job = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot2.bot.start(bot2.token, Bot=True), loop))
job.start()

loop.run_forever()