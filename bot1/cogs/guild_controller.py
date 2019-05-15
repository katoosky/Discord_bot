import os

import discord
from discord.ext import commands


# 変数
version="3.0.0"

class GuildController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_perm_manage_channels(self, ctx):
        if not 0 < len([role for role in ctx.message.author.roles if role.permissions.manage_channels]):
            await ctx.channel.send('You can not manage channels.')

    async def check_exist_project(self, ctx, project):
        project_category = discord.utils.get(ctx.guild.categories, name=project)
        if project_category is None:
            await ctx.channel.send(f'Project "{project}" is not found.')
    
    def rename_project_name(self, project):
        return project.replace('.', '').replace(' ', '-').replace('!', '')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="ゲスト")
        await member.add_roles([role])

    @commands.command(aliases=['mp'], brief="Make a new project with a new role.")
    async def make_project(self, ctx, project: str):
        await self.check_perm_manage_channels(ctx)

        project = self.rename_project_name(project)
        await ctx.channel.send('Make project {0} to {1}.'.format(project, ctx.guild.name))
        # roleの作成
        category_role = await ctx.guild.create_role(
            name=project, 
            mentionable=True,
            reason="Created category by command.",
            colour=discord.Colour.from_rgb(45, 90, 74),
            permissions=discord.Permissions.none(),
        )

        # カテゴリーの作成
        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            category_role: discord.PermissionOverwrite(read_messages=True, connect=True),
        }
        category = await ctx.guild.create_category(project, overwrites=overwrites)

        # チャンネルの作成
        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            category_role: discord.PermissionOverwrite(send_messages=False),
        }
        outline = await ctx.guild.create_text_channel(f'カテゴリ概要_{project}', category=category, overwrites=overwrites)
        await ctx.guild.create_text_channel(f'仕様情報_{project}', category=category, overwrites=overwrites)
        await ctx.guild.create_text_channel(f'連絡_{project}', category=category)
        await ctx.guild.create_text_channel(f'相談・話し合い_{project}', category=category)
        await ctx.guild.create_text_channel(f'雑談_{project}', category=category)
        await ctx.guild.create_text_channel(f'アイディア_{project}', category=category)
        await ctx.guild.create_text_channel(f'デバッグ_{project}', category=category)
        await ctx.guild.create_text_channel(f'システム通知_{project}', category=category)
        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, read_message_history=False),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False),
            category_role: discord.PermissionOverwrite(read_messages=True,  read_message_history=False),
        }
        await ctx.guild.create_text_channel('temporary', category=category, overwrites=overwrites)
        await ctx.guild.create_voice_channel(project, category=category)

        await outline.send(format_category_outline(category))
        await ctx.channel.send('Complete making project {0} to {1}.'.format(project, ctx.guild.name))

    @commands.command(aliases=['rp'], brief="Remove a project.")
    async def remove_project(self, ctx, project: str):
        await self.check_perm_manage_channels(ctx)

        project = self.rename_project_name(project)
        await self.check_exist_project(ctx, project)
        await ctx.channel.send('Remove project {0} from {1}.'.format(project, ctx.guild.name))
        project_role = discord.utils.get(ctx.guild.roles, name=project)
        await project_role.delete()
        project_category = discord.utils.get(ctx.guild.categories, name=project)
        for channel in project_category.channels:
            await channel.delete()
        await project_category.delete()
    
        await ctx.channel.send('Complete removing project {0} from {1}.'.format(project, ctx.guild.name))

    @commands.command(aliases=['ap'], brief="Archive a project.")
    async def archive_project(self, ctx, project: str):
        await self.check_perm_manage_channels(ctx)
        project = self.rename_project_name(project)

        await self.check_exist_project(ctx, project)
        await ctx.channel.send('Archive project {0} from {1} to "Archive".'.format(project, ctx.guild.name))
        archive = discord.utils.get(ctx.guild.categories, name='Archive')
        if archive is None:
            archive = await ctx.guild.create_category('Archive')
            await ctx.channel.send(f'Create archive category.')
        project_category = discord.utils.get(ctx.guild.categories, name=project)
        for channel in project_category.channels:
            if channel.name == 'temporary' or isinstance(channel, discord.VoiceChannel):
                await channel.delete()
            else:
                await channel.edit(category=archive)
        await project_category.delete()
    
        await ctx.channel.send('Complete archiving project {0} from {1} to "Archive".'.format(project, ctx.guild.name))
    
    @commands.command(aliases=['rap'], brief="Remove archived a project.")
    async def remove_archived_project(self, ctx, project: str):
        await self.check_perm_manage_channels(ctx)
        project = self.rename_project_name(project)

        await ctx.channel.send(f'Remove archived project {project} from "Archive" in {ctx.guild.name}.')
        archive = discord.utils.get(ctx.guild.categories, name='Archive')
        if archive is None:
            await ctx.channel.send(f'Archive category is not found.')
            return
        project_role = discord.utils.get(ctx.guild.roles, name=project)
        await project_role.delete()
        for channel in archive.channels:
            if channel.name.endswith(f'_{project}'):
                await channel.delete()
    
        await ctx.channel.send(f'Complete removing archived project {project} from "Archive" in {ctx.guild.name}.')
    
    @commands.command()
    async def get_channels(self, ctx):
        print(ctx.guild.categories[0].channels)


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

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(GuildController(bot))