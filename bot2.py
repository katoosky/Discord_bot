from datetime import date
import random

import discord
from discord.ext import commands
import psycopg2
from psycopg2.extras import DictCursor

# 変数
version="1.0.0"
token = "NDkzOTI2MDI4NjIwODU3MzY0.DosFJA.1Hzepp-iPyU-MFk__HZ9-JKsY8g"
bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"),
                   description='This is Botくん2号.')
bot.remove_command('help')

# dsn = "postgres://owdrwmlniladba:f2b7dfd2b785fc2d84bdd2dddd5bfbb458dfca2c22f72eab13a0b0be71d3b0f6@ec2-107-21-98-165.compute-1.amazonaws.com:5432/de885umnk3t5cr"
dsn = "postgres://discord:password@postgres:5432/discord"


class ThemeBot:
    help_text = """
Botくん1号 Commands
    &info
        Show Bot informations.
    &three_topics NAME
        Generate three topics for sandaibanashi.
    &add_genre GENRE
        Add a new genre to database.
    &show_genres [LIMIT]
        Show genre list.
        If use LIMIT option, Show latest genres as many as the LIMIT option.
    &add_topic TOPIC
        Add a new topic to database.
    &show_topics [LIMIT]
        Show topic list.
        If use LIMIT option, Show latest topics as many as the LIMIT option.
"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send('```'+help_text+'```')

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

    @commands.command()
    async def three_topics(self, ctx):
        command = ctx.message.content.split()
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
        await ctx.send(embed=embed)

    @commands.command()
    async def add_genre(self, ctx):
        await ctx.send(self.add_record("genres", ctx))

    @commands.command()
    async def show_genres(self, ctx):
        await ctx.send(self.show_values('genres', ctx))

    @commands.command()
    async def add_topic(self, ctx):
        await ctx.send(self.add_record("topics", ctx))

    @commands.command()
    async def show_topics(self, ctx):
        await ctx.send(self.show_values('topics', ctx))

    def get_list(self, table, limit):
        values = self.fetchall(table)
        result = "```" + """
ID      VALUE
————————————————————————————————————————————
"""
        for i, value in enumerate(values[-limit:]):
            result += str(i).ljust(8) + value['value'] + '\n'
        result += "```"
        return result

    def show_values(self, table, ctx):
        command = ctx.message.content.split()
        limit = int(command[1]) if 1 < len(command) else 0
        return self.get_list(table, limit)

    def add_record(self, table, ctx):
        value = ctx.message.content.split()[1]
        result = []
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                # テーブルが存在するかチェック
                cur.execute("SELECT * FROM pg_tables where tablename='{0}'".format(table))
                if cur.fetchone() is None:
                    cur.execute("create table {0} (id serial, value varchar(50) unique)".format(table))
                    conn.commit()
                    result.append("create table '{0}'.".format(table))
                # レコードが存在するかチェックして追加
                cur.execute("SELECT * FROM {0} WHERE value = '{1}'".format(table, value))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO {0} (value) VALUES ('{1}')".format(table, value))
                    conn.commit()
                    result.append("add value '{1}' to '{0}'.".format(table, value))
                else:
                    result.append("value '{1}' is already exist in '{0}'.".format(table, value))

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

bot.add_cog(ThemeBot(bot))
# bot.run(token)
