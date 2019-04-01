import asyncio
from datetime import date, datetime
import os
import random

import discord
from discord.ext import commands
import psycopg2
from psycopg2.extras import DictCursor
from pytz import timezone

# 変数
version="1.3.0"
token = os.environ['BOT2_TOKEN']
bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"),
                   description='This is Botくん2号.')
bot.remove_command('help')

dns = os.environ['DATABASE_URL']
# dsn = "postgres://discord:password@postgres:5432/discord"

jst = timezone('Asia/Tokyo')

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
    async def help(self, ctx):
        await ctx.send('```'+self.help_text+'```')

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

    # 三題噺
    @commands.command()
    async def three_topics(self, ctx):
        await ctx.send(embed=self.get_three_topics(ctx.message))

    @commands.command()
    async def add_genres(self, ctx):
        await ctx.send(self.add_record(self.three_topics_table['ジャンル'], ctx.message.content.split()[1:]))

    @commands.command()
    async def show_genres(self, ctx):
        await ctx.send(self.show_values(self.three_topics_table['ジャンル'], ctx.message))

    @commands.command()
    async def del_genres(self, ctx):
        await ctx.send(self.del_record(self.three_topics_table['ジャンル'], ctx.message.content.split()[1:]))

    @commands.command()
    async def add_topics(self, ctx):
        await ctx.send(self.add_record(self.three_topics_table['トピック'], ctx.message.content.split()[1:]))

    @commands.command()
    async def show_topics(self, ctx):
        await ctx.send(self.show_values(self.three_topics_table['トピック'], ctx.message))

    @commands.command()
    async def del_topics(self, ctx):
        await ctx.send(self.del_record(self.three_topics_table['トピック'], ctx.message.content.split()[1:]))

    # 絵のお題
    @commands.command()
    async def drawing(self, ctx):
        await ctx.send(embed=self.get_drawing(ctx.message))

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

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

"""
ここから下はメンションで操作するコマンド関連
"""
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
    add_help_tables(embed)

def add_help_tables(embed):
    embed.add_field(name="お絵かき 設定項目一覧",
                    value="、".join(ThemeBot.drawing_table.keys()),
                    inline=False)


def help_mention():
    embed = discord.Embed(title="Botくん2号", description='Bot2号くんです！（1号も一応いる）\n話しかけると創作のためのお題を出すよ！\n**コマンドを使用するときは一時チャットかDMを使いましょう！**', color=0x74e6bc)
    embed.add_field(name="コマンドの紹介",
                    value="コマンドをいくつか紹介するよ！\nまずメンション*「@Botくん2号」*で話しかけよう！\n\n",
                    inline=False)
    embed.add_field(name="ヘルプ", value="*「@Botくん2号 ヘルプ」*って書き込むと、このヘルプが見られるよ！", inline=False)
    embed.add_field(name="三題噺", value="三題噺関連は*「@Botくん2号 三題噺」*から始まるよ！", inline=False)
    embed.add_field(name="お絵かき", value="お絵かき関連は*「@Botくん2号 お絵かき」*から始まるよ！", inline=False)
    add_help_three_topics(embed)
    add_help_drawing(embed)
    embed.add_field(name="Version", value=version)
    # give info about you here
    embed.add_field(name="Author", value="雅猫")
    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
    # give users a link to invite thsi bot to their server
    embed.add_field(name="Invite", value="https://discordapp.com/api/oauth2/authorize?client_id=493926028620857364&permissions=27712&scope=bot")
    return embed

async def manage_table(bot, message, commands, table):
    if not 2 < len(commands):
        await message.channel.send(bot.get_list(table))
    elif commands[2] == "追加":
        await message.channel.send(bot.add_record(table, commands[3:]))
    elif commands[2] == "削除":
        await message.channel.send(bot.del_record(table, commands[3:]))

# サブコマンド内容
async def mention_three_topics(message, commands):
    theme_bot = ThemeBot(bot)
    if commands[1] == "お題":
        message.content = f'three_topics {message.author.name}'
        await message.channel.send(f'{message.author.mention}', embed=theme_bot.get_three_topics(message))
    elif commands[1] == "ヘルプ":
        embed = discord.Embed(title="コマンドの使い方、三題噺編！", description='三題噺のお題に関するコマンドの使い方について説明するよ！', color=0x74e6bc)
        add_help_three_topics(embed)
        await message.channel.send(embed=embed)
    for key, table in theme_bot.three_topics_table.items():
        if commands[1] == key:
            await manage_table(theme_bot, message, commands, table)

async def mention_drawing(message, commands):
    theme_bot = ThemeBot(bot)
    if commands[1] == "お題":
        message.content = f'drawing {message.author.name}'
        await message.channel.send(f'{message.author.mention}', embed=theme_bot.get_drawing(message))
    elif commands[1] == "ヘルプ":
        embed = discord.Embed(title="コマンドの使い方、お絵かき編！", description='お絵かきのお題に関するコマンドの使い方について説明するよ！', color=0x74e6bc)
        add_help_drawing(embed)
        await message.channel.send(embed=embed)
    elif commands[1] == "設定項目":
        embed = discord.Embed(title="コマンドの使い方、お絵かきの設定項目", description='お絵かきの設定項目はこちら！', color=0x74e6bc)
        add_help_tables(embed)
        await message.channel.send(embed=embed)
    for key, table in theme_bot.drawing_table.items():
        if commands[1] == key:
            await manage_table(theme_bot, message, commands, table)

# ポモドーロタイマー
timer_table = 'pomodoro_timer'
STATE_NONE = 0
STATE_SPRINT = 1
STATE_REST = 2

def check_timer_table():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pg_tables where tablename=%s", (timer_table,))
            if cur.fetchone() is None:
                cur.execute("""create table %s (
                    user_id bigint, tomato integer default 0, state smallint default 0, 
                    updated_at timestamp default current_timestamp, created_at timestamp default current_timestamp)"""
                    , (timer_table,))
                conn.commit()

def get_timer_record(user_id):
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            # テーブルが存在するかチェック
            cur.execute(f"SELECT * FROM %s WHERE user_id = %s", (timer_table, user_id))
            return cur.fetchone()

# 冗長だけど頻度は高くない想定なのでこのまま
def set_timer_record(user_id, state):
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            # ユーザが存在するかチェック
            cur.execute(f"SELECT * FROM %s WHERE user_id = %s", (timer_table, user_id))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO %s (user_id) VALUES (%s)", (timer_table, user_id))
                conn.commit()
            # レコードが存在するかチェックして追加
            cur.execute("""UPDATE %(table)s SET state=%(state)s, 
                updated_at=current_timestamp, WHERE user_id=%(user_id)s""",
                 {"table": timer_table, "user_id": user_id, "state": state})
            conn.commit()

def add_tomato(user_id):
    # 当日分の記録用のキャッシュを加算
    r = redis.from_url(os.environ.get("REDIS_URL"))
    r.incr(user_id)
    now = datetime.now(tz=jst)
    base_time = now.replace(minute=0, second=0, microsecond=0)
    r.expireat(user_id, base_time+timedelta(days=1))

    # DBの記録に加算
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE %(table)s SET tomato= tomato + %(amount)s, 
                updated_at=current_timestamp, WHERE user_id=%(user_id)s""",
                {"table": timer_table, "user_id": user_id, "amount": 1})
            conn.commit()

def get_tomato(user_id):
    r = redis.from_url(os.environ.get("REDIS_URL"))
    today_tomato = r.get(user_id)
    today_tomato = today_tomato if today_tomato is not None else 0
    tomato = get_timer_record(message.author.id)['tomato']
    return tomato, today_tomato

async def sprint(message):
    # スプリント開始処理
    set_timer_record(message.author.id, STATE_SPRINT)
    tomato, today_tomato = get_tomato(message.author.id)
    description = "25分集中して作業を頑張ろう！"
    embed = discord.Embed(title="ポモドーロタイマー", description=description, color=0xf31105)
    embed.add_field(name="今日のトマト", value=today_tomato)
    embed.add_field(name="これまでのトマト", value=tomato)
    await message.channel.send(f'{message.author.mention}', embed=embed)

    # ウェイト
    await asyncio.sleep(10)
    
    # スプリント終了処理
    if get_timer_record(message.author.id)['state'] == STATE_SPRINT:
        add_tomato(message.author.id)
        set_timer_record(message.author.id, STATE_NONE)
        tomato, today_tomato = get_tomato(message.author.id)
        description = "25分経ったよ！お疲れさま\nトマトはこれだけたまったよ！"
        embed = discord.Embed(title="ポモドーロタイマー", description=description, color=0xf31105)
        embed.add_field(name="今日のトマト", value=today_tomato)
        embed.add_field(name="これまでのトマト", value=tomato)
        await message.channel.send(f'{message.author.mention}', embed=embed)

async def rest(message):
    if get_timer_record(message.author.id).get('state', 0) == STATE_SPRINT:
        await message.channel.send(f'{message.author.mention} タイマーを中止するね......')
    set_timer_record(message.author.id, STATE_REST)
    await message.channel.send(f'{message.author.mention} 今から5分間休憩だよ！ゆっくり休んでリフレッシュ！')

    await asyncio.sleep(10)

    if get_timer_record(message.author.id).get('state', 0) == STATE_REST:
        set_timer_record(message.author.id, STATE_NONE)
        await message.channel.send(f'{message.author.mention} 休憩終了だよ！次も頑張ろう！')

async def rest(message):
    if get_timer_record(message.author.id).get('state', 0) in (STATE_SPRINT, STATE_REST):
        set_timer_record(message.author.id, STATE_NONE)
        await message.channel.send(f'{message.author.mention} タイマーを中止するね......')
    else:
        await message.channel.send(f'{message.author.mention} タイマーは動いてないよ？')

async def tomato(message):
    tomato, today_tomato = get_tomato(message.author.id)
    description = "あなたのトマトはこのくらいたまってるよ！"
    embed = discord.Embed(title="ポモドーロタイマー", description=description, color=0xf31105)
    embed.add_field(name="今日のトマト", value=today_tomato)
    embed.add_field(name="これまでのトマト", value=tomato)
    await message.channel.send(f'{message.author.mention}', embed=embed)

# DBの処理周りが冗長だけど、使用頻度は高くない想定なのでこのまま
async def mention_timer(message, commands):
    check_timer_table()

    if len(commands) == 1:
        await splint(message)
    else:
        if commands[1] == "休憩":
            await rest(message)
        elif commands[1] == "中止":
            await stop(message)
        elif commands[1] == "トマト":
            await tomato(message)

@bot.event # イベントを受信するための構文（デコレータ）
async def on_message(message):
    ctx = await bot.get_context(message)
    # コマンドだったらコマンドの処理
    if ctx.command is not None:
        await bot.process_commands(message)
    if not 0 < len([ member for member in message.mentions if member.id == bot.user.id]):
        return

    # メンションだけだったら返事を返す
    arg = message.content.split()
    if len(arg) == 1:
        await message.channel.send(f'やあ{message.author.mention}さん！元気かい？\nヘルプを見る場合は*「@Botくん2号 ヘルプ」*って書き込んでね！\n**コマンドを使用するときは一時チャットかDMを使いましょう！**')
        return

    # メンションでのコマンド実行だったらメンション用の関数を呼び出す
    commands = arg[1:]
    if commands[0] == "ヘルプ":
        await message.channel.send(embed=help_mention())
    elif commands[0] == "三題噺":
        await mention_three_topics(message, commands)
    elif commands[0] == "お絵かき" or commands[0] == "お絵描き":
        await mention_drawing(message, commands)
    elif commands[0] == "タイマー":
        await mention_timer(message, commands)


bot.add_cog(ThemeBot(bot))
# bot.run(token)
