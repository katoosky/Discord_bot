import asyncio
from threading import Thread

from bot1.bot import Bot1
from bot2.bot import Bot2

loop = asyncio.get_event_loop()
# botくん1号の起動
print("Start bot1.")
bot1 = Bo1()
job1 = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot1.start(Bot1.TOKEN, Bot=True), loop))

# botくん2号の起動
print("Start bot2.")
bot2 = Bot2()
job2 = Thread(target=asyncio.run_coroutine_threadsafe, args=(bot2.start(Bot2.TOKEN, Bot=True), loop))

job1.start()
job2.start()

loop.run_forever()