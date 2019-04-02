import asyncio
from threading import Thread

import bot1
import bot2

# loop = asyncio.get_event_loop()
# botくん1号の起動
print("Start bot1.")
# job1 = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot1.bot.start(bot1.token, Bot=True), loop))
job1 = Thread(target=bot1.bot.run, args=(bot1.token,))

# botくん2号の起動
print("Start bot2.")
# job2 = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot2.bot.start(bot2.token, Bot=True), loop))
job2 = Thread(target=bot2.bot.run, args=(bot2.token,))

job1.start()
job2.start()

# loop.run_forever()