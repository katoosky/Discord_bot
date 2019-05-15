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
        'bot2.cogs.quote',
        'bot2.cogs.theme',
        'bot2.cogs.timer',
        'bot2.cogs.reaction',
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
        ctx = await self.get_context(message)
        # コマンドだったらコマンドの処理
        
        if message.author.bot: # メッセージの送信者がBotなら、処理を終了する。
            return
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Command not found')
        else:
            print(f'```A error is occured\n{error}\n{"".join(traceback.format_tb(error.__traceback__))}```')

bot = Bot2()
# bot.run(Bot2.TOKEN)

