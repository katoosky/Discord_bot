import asyncio
from threading import Thread

import bot1

loop = asyncio.get_event_loop()
# bot1の起動
job = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot1.bot.start(bot1.token, Bot=True), loop))
job.start()


loop.run_forever()