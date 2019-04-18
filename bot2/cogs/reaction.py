from datetime import datetime

import discord # discord.pyをインポート
from discord.ext import commands # Bot Commands Frameworkのインポート


# コグとして用いるクラスを定義。
class Reaction(commands.Cog):
    # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("シージ") or message.content.startswith("しーじ"):
            await message.add_reaction('🌈')
            await message.add_reaction('6\u20e3')


# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Reaction(bot))