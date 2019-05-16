import os
import traceback

import discord
from discord.ext import commands


class Bot1(commands.Bot):
    TOKEN = os.environ['DISCORD_BOT_TOKEN_1']
    INITIAL_COGS = [
        'bot1.cogs.guild_controller',
        'bot1.cogs.meta',
    ]

    # MyBotのコンストラクタ。
    def __init__(self, *args, **kwargs):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            description='This is Botくん1号 for managing guild "KIDDING KID".',
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
        if message.author.bot: # メッセージの送信者がBotなら、処理を終了する。
            return
        if message.guild.id != 438704457266757643:
            await message.channel.send("このサーバーでは利用できません.")
            return
        await self.process_commands(message) # messageがコマンドなら実行する処理。

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Command not found')
        else:
            print(f'```A error is occured\n{error}\n{"".join(traceback.format_tb(error.__traceback__))}```'))
            await ctx.send('Error is occured')


bot = Bot1()
# bot.run(Bot1.TOKEN)