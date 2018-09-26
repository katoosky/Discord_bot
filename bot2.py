from datetime import date
import random

import discord
from discord.ext import commands
import psycopg2
from psycopg2.extras import DictCursor

# 変数
version="1.1.6"
token = "NDkzOTI2MDI4NjIwODU3MzY0.DosFJA.1Hzepp-iPyU-MFk__HZ9-JKsY8g"
bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"),
                   description='This is Botくん2号.')
bot.remove_command('help')

dsn = "postgres://owdrwmlniladba:f2b7dfd2b785fc2d84bdd2dddd5bfbb458dfca2c22f72eab13a0b0be71d3b0f6@ec2-107-21-98-165.compute-1.amazonaws.com:5432/de885umnk3t5cr"
# dsn = "postgres://discord:password@postgres:5432/discord"


class ThemeBot:
    help_text = """
Botくん1号 Commands
    &info
        Show Bot informations.
    &three_topics NAME
        Generate three topics for sandaibanashi.
    &add_genres GENRE [GENRE ...]
        Add new genres to database.
    &show_genres [LIMIT]
        Show genre list.
        If use LIMIT option, Show latest genres as many as the LIMIT option.
    &del_genres GENRE [GENRE ...]
        Delete genres.
    &add_topics TOPIC [TOPIC ...]
        Add new topics to database.
    &show_topics [LIMIT]
        Show topic list.
        If use LIMIT option, Show latest topics as many as the LIMIT option.
    &del_genres TOPIC [TOPIC ...]
        Delete topics.
"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send('```'+self.help_text+'```')

    @commands.command()
    async def info(self, ctx):
        """Show Bot informations."""
        embed = discord.Embed(title="Botくん2号", description='This is Botくん2号. This bot suggest a theme of creation.\nSend "!help", you can show commands.', color=0x74e6bc)
        embed.add_field(name="Version", value=version)
        # give info about you here
        embed.add_field(name="Author", value="雅猫")
        # Shows the number of servers the bot is member of.
        embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
        # give users a link to invite thsi bot to their server
        embed.add_field(name="Invite", value="https://discordapp.com/api/oauth2/authorize?client_id=493926028620857364&permissions=27712&scope=bot")
        await ctx.send(embed=embed)

    # 三題噺
    @commands.command()
    async def three_topics(self, ctx):
        await ctx.send(embed=self.get_three_topics(ctx.message))

    @commands.command()
    async def add_genres(self, ctx):
        await ctx.send(self.add_record("genres", ctx.message.content.split()[1:]))

    @commands.command()
    async def show_genres(self, ctx):
        await ctx.send(self.show_values('genres', ctx.message))

    @commands.command()
    async def del_genres(self, ctx):
        await ctx.send(self.del_record('genres', ctx.message.content.split()[1:]))

    @commands.command()
    async def add_topics(self, ctx):
        await ctx.send(self.add_record("topics", ctx.message.content.split()[1:]))

    @commands.command()
    async def show_topics(self, ctx):
        await ctx.send(self.show_values('topics', ctx.message))

    @commands.command()
    async def del_topics(self, ctx):
        await ctx.send(self.del_record('topics', ctx.message.content.split()[1:]))

    # 絵のお題

    def get_three_topics(self, message):
        command = message.content.split()
        user = command[1] if 1 < len(command) else None
        if user is not None:
            random.seed(date.today().strftime('%Y%m%d')+user)
        genre = random.sample(self.fetchall('genres'), 1)
        topics = random.sample(self.fetchall('topics'), 3)

        title = "今日の{0}さんのお題".format(user) if user is not None else "お題"
        description = "今日の{0}さんのお題はこちら！\n".format(user) if user is not None else ""
        description += "面白いお話期待してるよ！"
        embed = discord.Embed(title=title, description=description, color=0x74e6bc)
        embed.add_field(name="ジャンル", value=genre[0]['value'], inline=False)
        embed.add_field(name="1つ目のお題", value=topics[0]['value'])
        embed.add_field(name="2つ目のお題", value=topics[1]['value'])
        embed.add_field(name="3つ目のお題", value=topics[2]['value'])
        return embed

    def get_list(self, table, limit=0):
        values = self.fetchall(table)
        result = f"```table: {table}" + """
ID      VALUE
————————————————————————————————————————————
"""
        for i, value in enumerate(values[-limit:]):
            result += str(i).ljust(8) + value['value'] + '\n'
        result += "```"
        return result

    def show_values(self, table, message):
        command = message.content.split()
        limit = int(command[1]) if 1 < len(command) else 0
        return self.get_list(table, limit)

    def add_record(self, table, values):
        result = []
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                # テーブルが存在するかチェック
                cur.execute("SELECT * FROM pg_tables where tablename='{0}'".format(table))
                if cur.fetchone() is None:
                    cur.execute("create table {0} (id serial, value varchar(50) unique)".format(table))
                    conn.commit()
                    result.append("create table '{0}'.".format(table))
                for value in values:
                    # レコードが存在するかチェックして追加
                    cur.execute("SELECT * FROM {0} WHERE value = '{1}'".format(table, value))
                    if cur.fetchone() is None:
                        cur.execute("INSERT INTO {0} (value) VALUES ('{1}')".format(table, value))
                        conn.commit()
                        result.append("add value '{1}' to '{0}'.".format(table, value))
                    else:
                        result.append("value '{1}' is already exist in '{0}'.".format(table, value))

        return '```'+"\n".join(result)+'```'

    def del_record(self, table, values):
        result = []
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                # テーブルが存在するかチェック
                cur.execute("SELECT * FROM pg_tables where tablename='{0}'".format(table))
                if cur.fetchone() is None:
                    result.append("table '{0}' is not exist.".format(table))
                    return '```'+"\n".join(result)+'```'
                for value in values:
                    # レコードが存在するかチェックして追加
                    cur.execute("SELECT * FROM {0} WHERE value = '{1}'".format(table, value))
                    if cur.fetchone() is None:
                        result.append("value '{1}' is not exist in '{0}'.".format(table, value))
                    else:
                        cur.execute("DELETE FROM {0} WHERE value = '{1}'".format(table, value))
                        conn.commit()
                        result.append("delete value '{1}' from '{0}'.".format(table, value))

        return '```'+"\n".join(result)+'```'
    
    def fetchall(self, table):
        with psycopg2.connect(dsn) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute('SELECT * FROM {0}'.format(table))
                return cur.fetchall()

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

@bot.event
async def on_guild_join(guild):
    await guild.system_channel.send('初めましてBotくん2号だよ\nヘルプを見る場合は*「@Botくん2号 ヘルプ」*って書き込んでね！\n**コマンドを使用するときは一時チャットかDMを使いましょう**')

def add_help_three_topics(embed):
    embed.add_field(name="@Botくん2号 三題噺",
                    value="*「@Botくん2号 三題噺 お題」*であなたの今日のお題を出すよ！\n \
                    *「@Botくん2号 三題噺 ジャンル」*で登録されてる**ジャンル**を確認できるよ！\n \
                    *「@Botくん2号 三題噺 ジャンル 追加」*の後に「 」半角スペース区切りでジャンルを書き込むとジャンルを登録できるよ！\n \
                    *「@Botくん2号 三題噺 ジャンル 削除」*の後に「 」半角スペース区切りでジャンルを書き込むと指定したジャンルを消せるよ！\n \
                    例えば、*「@Botくん2号 三題噺 ジャンル 追加 シリアス ほのぼの」*みたいな感じだよ！\n \
                    「ジャンル」を「トピック」に変えて書き込むと三題噺のお題である**トピック**について扱うことができるよ！\n\n \
                    いろんな言葉を追加していってね！",
                    inline=False)

def add_help_drawing(embed):
    embed.add_field(name="@Botくん2号 お絵かき",
                    value="*「@Botくん2号 お絵かき お題」*であなたの今日のお題を出すよ！\n \
                    お絵かきのお題ではキャラクターの設定の中から5つの設定をお題として出すよ！\n \
                    *「@Botくん2号 お絵かき [設定]」*で登録されてるキャラクターの設定を確認できるよ！\n \
                    設定の種類は下の方に書いてあるからそれを参考に[設定]の部分を置き換えてね\n \
                    *「@Botくん2号 お絵かき [設定] 追加」*の後に「 」半角スペース区切りで設定を書き込むと設定を登録できるよ！\n \
                    *「@Botくん2号 お絵かき [設定] 削除」*の後に「 」半角スペース区切りで設定を書き込むと指定した設定を消せるよ！\n \
                    例えば、*「@Botくん2号 お絵かき 特徴 追加 狐耳 エルフ耳」*みたいな感じだよ！\n\n \
                    いろんな設定を追加していってね！",
                    inline=False)
    embed.add_field(name="お絵かき 設定項目一覧",
                    value="キャラクター、種族、性別、髪型、髪色、体型、性格、服装、特徴、モチーフ、ポーズ、シチュエーション",
                    inline=False)

def help_mention():
    embed = discord.Embed(title="Botくん2号", description='Bot2号くんです！（1号も一応いる）\n話しかけると創作のためのお題を出すよ！\n**コマンドを使用するときは一時チャットかDMを使いましょう！**', color=0x74e6bc)
    embed.add_field(name="コマンドの紹介",
                    value="コマンドをいくつか紹介するよ！\nまずメンション*「@Botくん2号」*で話しかけよう！\n\n",
                    inline=False)
    embed.add_field(name="ヘルプ", value="*「@Botくん2号 ヘルプ」*って書き込むと、このヘルプが見られるよ！", inline=False)
    embed.add_field(name="三題噺", value="三題噺関連は*「@Botくん2号 三題噺」*から始まるよ！", inline=False)
    embed.add_field(name="お絵かき", value="お絵かき関連は*「@Botくん2号 お絵かき」*から始まるよ！\nでも、まだ未実装なんだ......ごめんね？", inline=False)
    add_help_three_topics(embed)
    # add_help_drawing(embed)
    embed.add_field(name="Version", value=version)
    # give info about you here
    embed.add_field(name="Author", value="雅猫")
    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
    # give users a link to invite thsi bot to their server
    embed.add_field(name="Invite", value="https://discordapp.com/api/oauth2/authorize?client_id=493926028620857364&permissions=27712&scope=bot")
    return embed

@bot.event # イベントを受信するための構文（デコレータ）
async def on_message(message):
    if not 0 < len([ member for member in message.mentions if member.id == bot.user.id]):
        return

    arg = message.content.split()
    if len(arg) == 1:
        await message.channel.send(f'やあ{message.author.mention}さん！元気かい？\nヘルプを見る場合は*「@Botくん2号 ヘルプ」*って書き込んでね！\n**コマンドを使用するときは一時チャットかDMを使いましょう！**')
        return

    theme_bot = ThemeBot(bot)
    commands = arg[1:]
    if commands[0] == "ヘルプ":
        await message.channel.send(embed=help_mention())
    elif commands[0] == "三題噺":
        if commands[1] == "お題":
            message.content = f'three_topics {message.author.name}'
            await message.channel.send(f'{message.author.mention}', embed=theme_bot.get_three_topics(message))
        elif commands[1] == "ヘルプ":
            embed = discord.Embed(title="コマンドの使い方、三題噺編！", description='三題噺のお題に関するコマンドの使い方について説明するよ！', color=0x74e6bc)
            add_help_three_topics(embed)
            await message.channel.send(embed=embed)
        elif commands[1] == "ジャンル":
            if not 2 < len(commands):
                await message.channel.send(theme_bot.get_list('genres'))
            elif commands[2] == "追加":
                await message.channel.send(theme_bot.add_record('genres', commands[3:]))
            elif commands[2] == "削除":
                await message.channel.send(theme_bot.del_record('genres', commands[3:]))
        elif commands[1] == "トピック":
            if not 2 < len(commands):
                await message.channel.send(theme_bot.get_list('topics'))
            elif commands[2] == "追加":
                await message.channel.send(theme_bot.add_record('topics', commands[3:]))
            elif commands[2] == "削除":
                await message.channel.send(theme_bot.del_record('topics', commands[3:]))
    elif commands[0] == "お絵かき" or commands[0] == "お絵描き":
        if commands[1] == "お題":
            pass
        elif commands[1] == "ヘルプ":
            embed = discord.Embed(title="コマンドの使い方、お絵かき編！", description='**まだ実装中です**\nお絵かきのお題に関するコマンドの使い方について説明するよ！', color=0x74e6bc)
            add_help_drawing(embed)
            await message.channel.send(embed=embed)
        elif commands[1] == "キャラクター":
            pass
        elif commands[1] == "種族":
            pass
        elif commands[1] == "性別":
            pass
        elif commands[1] == "髪型":
            pass
        elif commands[1] == "髪色":
            pass
        elif commands[1] == "体型":
            pass
        elif commands[1] == "性格":
            pass
        elif commands[1] == "服装":
            pass
        elif commands[1] == "特徴":
            pass
        elif commands[1] == "モチーフ":
            pass
        elif commands[1] == "ポーズ":
            pass
        elif commands[1] == "シチュエーション":
            pass


bot.add_cog(ThemeBot(bot))
# bot.run(token)
