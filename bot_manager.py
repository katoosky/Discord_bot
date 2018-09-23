from threading import Thread

import bot1

# bot1の起動
Thread(target=bot1.bot.run, args=(bot1.token,)).start()