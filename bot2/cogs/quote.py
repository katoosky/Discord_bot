from datetime import datetime
import re

import discord # discord.pyをインポート
from discord.ext import commands # Bot Commands Frameworkのインポート

pattern = r"https://discordapp.com/channels/\d+/\d+/\d+"
repattern = re.compile(pattern)

# コグとして用いるクラスを定義。
class Quote(commands.Cog):
    # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    async def quote_message(self, message, guild_id, channel_id, message_id):
        print(guild_id, channel_id, message_id)
        channel = self.bot.get_channel(int(channel_id))
        print(channel)
        if channel is None:
            await message.channel.send("メッセージへの権限がありません。")
        else:
            target = await channel.fetch_message(message_id)
            embed = discord.Embed(description=target.content, timestamp=datetime.now())
            embed.set_author(name=target.author.name, icon_url=target.author.avatar_url)
            embed.set_footer(text="via discordbot")
            await message.channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        quote = self.bot.get_cog('Quote')
        if quote is not None:
            for match in repattern.finditer(message.content):
                print(f"quote message: {match.group()}")
                messages = match.group().split('/')
                print(messages)
                await quote.quote_message(message, *messages[4:])

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Quote(bot))