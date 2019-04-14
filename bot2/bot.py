import asyncio
from datetime import date, datetime, timedelta
import os
import random
import traceback

import discord
from discord.ext import commands
import psycopg2
from psycopg2.extras import DictCursor
from pytz import timezone
import redis


# 変数
version="2.0.0"


class Bot2(commands.Bot):
    TOKEN = os.environ['DISCORD_BOT_TOKEN_2']
    INITIAL_COGS = [
        'cogs.quote',
        'cogs.theme',
        'cogs.timer'
    ]

    # MyBotのコンストラクタ。
    def __init__(self, *args, **kwargs):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(
            command_prefix=commands.when_mentioned,
            description='This is Botくん2号.',
            *args, **kwargs)

        # INITIAL_COGSに格納されている名前から、コグを読み込む。
        # エラーが発生した場合は、エラー内容を表示。
        for cog in self.__class__.INITIAL_COGS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()    # Botの準備完了時に呼び出されるイベント

    async def on_ready(self):
        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')

    # メッセージを受信した際に呼び出されるイベント
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        # コマンドだったらコマンドの処理
        
        if message.author.bot: # メッセージの送信者がBotなら、処理を終了する。
            return
        await self.process_commands(message)
        # else:
        #     # メンションだけだったら返事を返す
        #     arg = message.content.split()
        #     if len(arg) == 1:
        #         await message.channel.send(f'やあ{message.author.mention}さん！元気かい？\nヘルプを見る場合は*「@Botくん2号 ヘルプ」*って書き込んでね！\n**コマンドを使用するときは一時チャットかDMを使いましょう！**')
        #         return

        #     # メンションでのコマンド実行だったらメンション用の関数を呼び出す
        #     commands = arg[1:]
        #     if commands[0] == "ヘルプ":
        #         await message.channel.send(embed=help_mention())
        #     elif commands[0] == "三題噺":
        #         await mention_three_topics(message, commands)
        #     elif commands[0] == "お絵かき" or commands[0] == "お絵描き":
        #         await mention_drawing(message, commands)
        #     elif commands[0] == "タイマー":
        #         await mention_timer(message, commands)



bot = Bot2()
bot.run(Bot2.TOKEN)

