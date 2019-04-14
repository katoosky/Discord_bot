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

# コグとして用いるクラスを定義。
class Timer(commands.Cog):
    # ポモドーロタイマー
    TIMER_TABLE = 'pomodoro_timer'
    STATE_NONE = 0
    STATE_SPRINT = 1
    STATE_REST = 2

    # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    def check_timer_table(self):
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM pg_tables where tablename=%s", (self.__class__.TIMER_TABLE,))
                if cur.fetchone() is None:
                    cur.execute(f"""create table {self.__class__.TIMER_TABLE} ( 
                        user_id bigint, tomato integer default 0, state smallint default 0, 
                        updated_at timestamp default current_timestamp, created_at timestamp default current_timestamp)""")
                    conn.commit()

    def get_timer_record(self, user_id):
        with psycopg2.connect(dsn) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # テーブルが存在するかチェック
                cur.execute(f"SELECT * FROM {self.__class__.TIMER_TABLE} WHERE user_id = %s", (user_id,))
                return cur.fetchone()

    # 冗長だけど頻度は高くない想定なのでこのまま
    def set_timer_record(self, user_id, state):
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                # ユーザが存在するかチェック
                cur.execute(f"SELECT * FROM {self.__class__.TIMER_TABLE} WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    cur.execute(f"INSERT INTO {self.__class__.TIMER_TABLE} (user_id) VALUES (%s)", (user_id,))
                    conn.commit()
                # レコードが存在するかチェックして追加
                cur.execute(f"""UPDATE {self.__class__.TIMER_TABLE} SET state=%(state)s, 
                    updated_at=current_timestamp WHERE user_id=%(user_id)s""",
                    {"user_id": user_id, "state": state})
                conn.commit()

    def add_tomato(self, user_id):
        # 当日分の記録用のキャッシュを加算
        r = redis.from_url(os.environ.get("REDIS_URL"))
        r.incr(user_id)
        now = datetime.now(tz=jst).replace(tzinfo=jst)
        base_time = now.replace(minute=0, second=0, microsecond=0)
        r.expireat(user_id, base_time+timedelta(days=1))

        # DBの記録に加算
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""UPDATE {self.__class__.TIMER_TABLE} SET tomato= tomato + %(amount)s, 
                    updated_at=current_timestamp WHERE user_id=%(user_id)s""",
                    {"user_id": user_id, "amount": 1})
                conn.commit()

    def get_tomato(self, user_id):
        r = redis.from_url(os.environ.get("REDIS_URL"))
        today_tomato = r.get(user_id)
        today_tomato = int(today_tomato) if today_tomato is not None else 0
        tomato = self.get_timer_record(user_id)
        tomato = tomato['tomato'] if tomato is not None else 0
        return tomato, today_tomato

    async def sprint(self, message):
        # スプリント開始処理
        self.set_timer_record(message.author.id, self.__class__.STATE_SPRINT)
        tomato, today_tomato = self.get_tomato(message.author.id)
        description = "25分集中して作業を頑張ろう！"
        embed = discord.Embed(title="ポモドーロタイマー", description=description, color=0xf31105)
        embed.add_field(name="今日のトマト", value=today_tomato)
        embed.add_field(name="これまでのトマト", value=tomato)
        await message.channel.send(f'{message.author.mention}', embed=embed)

        # ウェイト
        # await asyncio.sleep(60 * 25)
        await asyncio.sleep(10)
        
        # スプリント終了処理
        if get_timer_record(message.author.id)['state'] == self.__class__.STATE_SPRINT:
            self.add_tomato(message.author.id)
            self.set_timer_record(message.author.id, self.__class__.STATE_NONE)
            tomato, today_tomato = self.get_tomato(message.author.id)
            description = "25分経ったよ！お疲れさま\nトマトはこれだけたまったよ！"
            embed = discord.Embed(title="ポモドーロタイマー", description=description, color=0xf31105)
            embed.add_field(name="今日のトマト", value=today_tomato)
            embed.add_field(name="これまでのトマト", value=tomato)
            await message.channel.send(f'{message.author.mention}', embed=embed)

    async def rest(self, message):
        record = get_timer_record(message.author.id)
        if  record is not None and record.get('state', 0) == self.__class__.STATE_SPRINT:
            await message.channel.send(f'{message.author.mention} タイマーを中止するね......')
        self.set_timer_record(message.author.id, self.__class__.STATE_REST)
        await message.channel.send(f'{message.author.mention} 今から5分間休憩だよ！ゆっくり休んでリフレッシュ！')

        # await asyncio.sleep(60 * 5)
        await asyncio.sleep(10)

        if self.get_timer_record(message.author.id).get('state', 0) == self.__class__.STATE_REST:
            self.set_timer_record(message.author.id, Sself.__class__.TATE_NONE)
            await message.channel.send(f'{message.author.mention} 休憩終了だよ！次も頑張ろう！')

    async def stop(self, message):
        record = self.get_timer_record(message.author.id)
        if record is not None and record.get('state', 0) in (self.__class__.STATE_SPRINT, self.__class__.STATE_REST):
            self.set_timer_record(message.author.id, self.__class__.STATE_NONE)
            await message.channel.send(f'{message.author.mention} タイマーを中止するね......')
        else:
            await message.channel.send(f'{message.author.mention} タイマーは動いてないよ？')

    async def tomato(self, message):
        tomato, today_tomato = self.get_tomato(message.author.id)
        description = "あなたのトマトはこのくらいたまってるよ！"
        embed = discord.Embed(title="ポモドーロタイマー", description=description, color=0xf31105)
        embed.add_field(name="今日のトマト", value=today_tomato)
        embed.add_field(name="これまでのトマト", value=tomato)
        await message.channel.send(f'{message.author.mention}', embed=embed)

    def calc_timedelta(self, td):
        if 59 < td.seconds:
            return int(td.seconds/60), td.seconds%60
        return 0, td.seconds

    async def remaining(self, message):
        now = datetime.now(tz=jst).replace(tzinfo=jst)
        record = self.get_timer_record(message.author.id)
        if record is None or record.get('state') == STATE_NONE:
            await message.channel.send(f'{message.author.mention} タイマーは動いてないよ')
        elif record.get('state') == STATE_SPRINT:
            remaining_time = record.get('updated_at').replace(tzinfo=jst) - now + timedelta(minutes=25)
            minute, second = self.calc_timedelta(remaining_time)
            await message.channel.send(f'{message.author.mention} タイマーは残り{minute}分{second}だよ')
        elif record.get('state') == STATE_REST:
            remaining_time = record.get('updated_at').replace(tzinfo=jst) - now + timedelta(minutes=5)
            minute, second = self.calc_timedelta(remaining_time)
            await message.channel.send(f'{message.author.mention} 休憩時間は残り{minute}分{second}だよ')

    # DBの処理周りが冗長だけど、使用頻度は高くない想定なのでこのまま
    @commands.command(name="タイマー")
    async def mention_timer(self, ctx):
        self.check_timer_table()

        # コマンドの分解する
        arg = ctx.message.content.split()
        commands = arg[1:]

        if len(commands) == 1:
            await self.sprint(ctx.message)
        else:
            if commands[1] == "休憩":
                await self.rest(ctx.message)
            elif commands[1] == "中止":
                await self.stop(ctx.message)
            elif commands[1] == "トマト":
                await self.tomato(ctx.message)
            elif commands[1] in  ("残り", "時間", "残り時間"):
                await self.remaining(ctx.message)
            

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Timer(bot))
