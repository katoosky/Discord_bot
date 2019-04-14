import asyncio
from datetime import date, datetime, timedelta
import os
import random
import traceback

import psycopg2
from psycopg2.extras import DictCursor
from pytz import timezone
import redis

import discord # discord.pyをインポート
from discord.ext import commands # Bot Commands Frameworkのインポート


dsn = os.environ['DATABASE_URL']
# dsn = "postgres://discord:password@postgres:5432/discord"
jst = timezone('Asia/Tokyo')


class Theme(commands.Cog):s
    three_topics_table = {
        'ジャンル': 'genres',
        'トピック': 'topics',
    }

    drawing_table = {
        'キャラクター': 'character',
        '種族': 'race',
        '性別': 'sex',
        '年齢': 'age',
        '髪型': 'hair_style',
        '髪色': 'hair_color',
        '瞳の色': 'eye_color',
        '体型': 'body',
        '性格': 'personality',
        '職業': 'job',
        '口癖': 'catch_phrase',
        '好きなもの': 'favorite',
        '嫌いなもの': 'dislike',
        '将来の夢': 'dream',
        '特技': 'skill',
        '服装': 'style',
        '特徴': 'characteristics',
        'モチーフ': 'motif',
        'ポーズ': 'pose',
        'シチュエーション': 'situation',
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """Show Bot informations."""
        embed = discord.Embed(title="Botくん2号", description='This is Botくん2号. This bot suggest a theme of creation.\nSend "&help", you can show commands.', color=0x74e6bc)
        embed.add_field(name="Version", value=version)
        # give info about you here
        embed.add_field(name="Author", value="雅猫")
        # Shows the number of servers the bot is member of.
        embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
        # give users a link to invite thsi bot to their server
        embed.add_field(name="Invite", value="https://discordapp.com/api/oauth2/authorize?client_id=493926028620857364&permissions=27712&scope=bot")
        await ctx.send(embed=embed)

    # 三題噺の関数
    def get_three_topics(self, message):
        command = message.content.split()
        user = command[1] if 1 < len(command) else None
        if user is not None:
            random.seed(date.today().strftime('%Y%m%d')+user)
        genre = random.sample(self.fetchall(self.three_topics_table['ジャンル']), 1)
        topics = random.sample(self.fetchall(self.three_topics_table['トピック']), 3)

        title = "今日の{0}さんのお題".format(user) if user is not None else "お題"
        description = "今日の{0}さんのお題はこちら！\n".format(user) if user is not None else ""
        description += "面白いお話期待してるよ！"
        embed = discord.Embed(title=title, description=description, color=0x74e6bc)
        embed.add_field(name="ジャンル", value=genre[0]['value'], inline=False)
        embed.add_field(name="1つ目のお題", value=topics[0]['value'])
        embed.add_field(name="2つ目のお題", value=topics[1]['value'])
        embed.add_field(name="3つ目のお題", value=topics[2]['value'])
        return embed

    # お絵かきの関数
    def get_drawing(self, message):
        command = message.content.split()
        user = command[1] if 1 < len(command) else None
        if user is not None:
            random.seed(date.today().strftime('%Y%m%d')+user)
        
        title = "今日の{0}さんのお題".format(user) if user is not None else "お題"
        description = "今日の{0}さんのお題はこちら！\n".format(user) if user is not None else ""
        description += "素敵なイラストを楽しみにしてるよ！"
        embed = discord.Embed(title=title, description=description, color=0x74e6bc)
        
        tables = {}
        drawing_table = self.drawing_table.copy()
        if (random.randrange(len(drawing_table)) == 0):
            tables['キャラクター'] = drawing_table['キャラクター']
            del drawing_table['種族']
            del drawing_table['性別']
            del drawing_table['髪色']
            del drawing_table['瞳の色']
            del drawing_table['性格']
            del drawing_table['口癖']
            del drawing_table['好きなもの']
            del drawing_table['嫌いなもの']
            del drawing_table['将来の夢']
        del drawing_table['キャラクター']
        
        PICKUP_NUM = 5
        tables.update({k:v for k, v in random.sample(drawing_table.items(), PICKUP_NUM-len(tables))})
        for name, table in tables.items():
            embed.add_field(name=name, value=random.choice(self.fetchall(table))['value'])
        return embed
        
    # 汎用関数
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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await guild.system_channel.send('初めましてBotくん2号だよ\nヘルプを見る場合は*「@Botくん2号 ヘルプ」*って書き込んでね！\n**コマンドを使用するときは一時チャットかDMを使いましょう**')


    def add_help_three_topics(self, embed):
        embed.add_field(name="@Botくん2号 三題噺",
                        value="*「@Botくん2号 三題噺 お題」*であなたの今日のお題を出すよ！\n \
                        *「@Botくん2号 三題噺 ジャンル」*で登録されてる**ジャンル**を確認できるよ！\n \
                        *「@Botくん2号 三題噺 ジャンル 追加」*の後に「 」半角スペース区切りでジャンルを書き込むとジャンルを登録できるよ！\n \
                        *「@Botくん2号 三題噺 ジャンル 削除」*の後に「 」半角スペース区切りでジャンルを書き込むと指定したジャンルを消せるよ！\n \
                        例えば、*「@Botくん2号 三題噺 ジャンル 追加 シリアス ほのぼの」*みたいな感じだよ！\n \
                        「ジャンル」を「トピック」に変えて書き込むと三題噺のお題である**トピック**について扱うことができるよ！\n\n \
                        いろんな言葉を追加していってね！",
                        inline=False)

    def add_help_drawing(self, embed):
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
        add_help_tables(embed)

    def add_help_tables(self, embed):
        embed.add_field(name="お絵かき 設定項目一覧",
                        value="、".join(Theme.drawing_table.keys()),
                        inline=False)

    @commands.group(name="ヘルプ")
    async def help_mention(self, ctx):
        embed = discord.Embed(title="Botくん2号", description='Bot2号くんです！（1号も一応いる）\n話しかけると創作のためのお題を出すよ！\n**コマンドを使用するときは一時チャットかDMを使いましょう！**', color=0x74e6bc)
        embed.add_field(name="コマンドの紹介",
                        value="コマンドをいくつか紹介するよ！\nまずメンション*「@Botくん2号」*で話しかけよう！\n\n",
                        inline=False)
        embed.add_field(name="ヘルプ", value="*「@Botくん2号 ヘルプ」*って書き込むと、このヘルプが見られるよ！", inline=False)
        embed.add_field(name="三題噺", value="三題噺関連は*「@Botくん2号 三題噺」*から始まるよ！", inline=False)
        embed.add_field(name="お絵かき", value="お絵かき関連は*「@Botくん2号 お絵かき」*から始まるよ！", inline=False)
        self.add_help_three_topics(embed)
        self.add_help_drawing(embed)
        embed.add_field(name="Version", value=version)
        # give info about you here
        embed.add_field(name="Author", value="雅猫")
        # Shows the number of servers the bot is member of.
        embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
        # give users a link to invite thsi bot to their server
        embed.add_field(name="Invite", value="https://discordapp.com/api/oauth2/authorize?client_id=493926028620857364&permissions=27712&scope=bot")
        await message.channel.send(embed=embed)

    async def manage_table(self, message, commands, table):
        if not 2 < len(commands):
            await message.channel.send(bot.get_list(table))
        elif commands[2] == "追加":
            await message.channel.send(bot.add_record(table, commands[3:]))
        elif commands[2] == "削除":
            await message.channel.send(bot.del_record(table, commands[3:]))

    # サブコマンド内容
    @commands.group(name="三題噺")
    async def mention_three_topics(self, ctx):
        message = ctx.message
        arg = message.content.split()
        commands = arg[1:]

        if commands[1] == "お題":
            message.content = f'three_topics {message.author.name}'
            await message.channel.send(f'{message.author.mention}', embed=self.get_three_topics(message))
        elif commands[1] == "ヘルプ":
            embed = discord.Embed(title="コマンドの使い方、三題噺編！", description='三題噺のお題に関するコマンドの使い方について説明するよ！', color=0x74e6bc)
            self.add_help_three_topics(embed)
            await message.channel.send(embed=embed)
        for key, table in self.three_topics_table.items():
            if commands[1] == key:
                await self.manage_table(message, commands, table)

    @commands.group(name="お絵かき")
    @commands.group(name="お絵描き")
    async def mention_drawing(self, ctx):
        message = ctx.message
        arg = message.content.split()
        commands = arg[1:]
        
        if commands[1] == "お題":
            message.content = f'drawing {message.author.name}'
            await message.channel.send(f'{message.author.mention}', embed=self.get_drawing(message))
        elif commands[1] == "ヘルプ":
            embed = discord.Embed(title="コマンドの使い方、お絵かき編！", description='お絵かきのお題に関するコマンドの使い方について説明するよ！', color=0x74e6bc)
            self.add_help_drawing(embed)
            await message.channel.send(embed=embed)
        elif commands[1] == "設定項目":
            embed = discord.Embed(title="コマンドの使い方、お絵かきの設定項目", description='お絵かきの設定項目はこちら！', color=0x74e6bc)
            self.add_help_tables(embed)
            await message.channel.send(embed=embed)
        for key, table in self.drawing_table.items():
            if commands[1] == key:
                await self.manage_table(message, commands, table)


# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Theme(bot))