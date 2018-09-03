import csv
import discord
from discord.ext import commands


# 変数
version="1.0.1"
token = "NDcyNTM5NzczMzI4ODE4MTc2.Dm0hmA.b4vSarQxZBcbp6rEJ545QsQyeu4"
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='This is Botくん1号 for managing guild "KIDDING KID".')
bot.remove_command('help')

def format_category_outline(category):
    text = """
```
デフォルトで生成されるチャンネルの説明です。
各カテゴリーで個別に作成したチャンネルは別レスでまとめてください
```
チャンネルの説明
　<#{0.id}>
　　このチャンネル

　<#{1.id}>
　　仕様情報をまとめるチャンネル
　　確定した仕様のみを上げる
　　未確定の仕様などは

　<#{2.id}>
　　全体連絡用のチャンネル

　<#{3.id}>
　　相談用チャンネル
　　必ず、何を相談したいか提起してから話し合う
　　5レス以上の話し合いは、終わったら内容をまとめる

　<#{4.id}>
　　雑談用チャンネル

　<#{5.id}>
　　アプリやサービスのアイディアをぶん投げてくチャンネル

　<#{6.id}>
　　バグの報告や修正報告など、デバッグに関することを投げるチャンネル

　<#{6.id}>
　　システム通知を表示するチャンネル
　　Botを実行する場合もここを使う

　<#{8.id}>
　　ログインしてるときのメッセージ以外見れないチャット
　　ログアウト時にログは見れなくなる
　　ログに残したくない怒りのメッセージや罵り合いなどはここで

　<#{9.id}>
　　ボイスチャット
　　会議や話し合いなどで使ってください
"""
    return text.format(*category.channels)

class GuildManager:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        help_context = []
        help_context.append('Botくん1号 Commands')
        help_context.append('\t!info')
        help_context.append('\t\tShow Bot informations.')
        help_context.append('\t!make_project PROJECT_NAME')
        help_context.append('\t\tMake a new project with a new role.')
        help_context.append('\t!remove_project PROJECT_NAME')
        help_context.append('\t\tRemove a project.')
        await ctx.send('```'+'\n'.join(help_context)+'```')

    @commands.command()
    async def info(self, ctx):
        """Show Bot informations."""
        embed = discord.Embed(title="Botくん1号", description='This is Botくん1号 for managing guild "KIDDING KID".', color=0x74e6bc)
        embed.add_field(name="Version", value=version)
        # give info about you here
        embed.add_field(name="Author", value="雅猫")
        # Shows the number of servers the bot is member of.
        embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
        # give users a link to invite thsi bot to their server
        embed.add_field(name="Invite", value="https://discordapp.com/api/oauth2/authorize?client_id=472539773328818176&permissions=0&scope=bot")
        await ctx.send(embed=embed)
    
    @commands.command()
    async def make_project(self, ctx):
        """
        Make a new project with a new role.
        Usage:	make_project PROJECT_NAME
        """
        if not 0 < len([role for role in ctx.message.author.roles if role.permissions.manage_channels]):
            await ctx.channel.send('You can not create new project.')
        project_name = ctx.message.content.split()[1]
        await ctx.channel.send('Make project {0} to {1}.'.format(project_name, ctx.guild.name))

        # roleの作成
        category_role = await ctx.guild.create_role(
            name=project_name, 
            mentionable=True,
            reason="Created category by command.",
            colour=discord.Colour.from_rgb(45, 90, 74),
            permissions=discord.Permissions.none(),
        )

        # カテゴリーの作成
        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.guild.role_hierarchy[1]: discord.PermissionOverwrite(read_messages=True, connect=True),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            category_role: discord.PermissionOverwrite(read_messages=True, connect=True),
        }
        category = await ctx.guild.create_category(project_name, overwrites=overwrites)

        # チャンネルの作成
        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.role_hierarchy[1]: discord.PermissionOverwrite(read_messages=True),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            category_role: discord.PermissionOverwrite(send_messages=False),
        }
        outline = await ctx.guild.create_text_channel('カテゴリ概要', category=category, overwrites=overwrites)
        await ctx.guild.create_text_channel('仕様情報', category=category, overwrites=overwrites)
        await ctx.guild.create_text_channel('連絡', category=category)
        await ctx.guild.create_text_channel('相談・話し合い', category=category)
        await ctx.guild.create_text_channel('雑談', category=category)
        await ctx.guild.create_text_channel('アイディア', category=category)
        await ctx.guild.create_text_channel('デバッグ', category=category)
        await ctx.guild.create_text_channel('システム通知', category=category)
        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, read_message_history=False),
            ctx.guild.role_hierarchy[1]: discord.PermissionOverwrite(read_messages=True, read_message_history=False),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False),
            category_role: discord.PermissionOverwrite(read_messages=True,  read_message_history=False),
        }
        await ctx.guild.create_text_channel('temporary', category=category, overwrites=overwrites)
        await ctx.guild.create_voice_channel(project_name, category=category)

        await outline.send(format_category_outline(category))

    @commands.command()
    async def remove_project(self, ctx):
        """
        Remove a project.
        Usage:	remove_project PROJECT_NAME
        """
        if not 0 < len([role for role in ctx.message.author.roles if role.permissions.manage_channels]):
            await ctx.channel.send('You can not create new project.')
        project_name = ctx.message.content.split()[1]
        await ctx.channel.send('Remove project {0} from {1}.'.format(project_name, ctx.guild.name))
        for role in ctx.guild.roles:
            if role.name == project_name:
                await role.delete()
        for category in ctx.guild.categories:
            if category.name == project_name:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()
    
    @commands.command()
    async def get_channels(self, ctx):
        print(ctx.guild.categories[0].channels)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(GuildManager(bot))
bot.run(token)