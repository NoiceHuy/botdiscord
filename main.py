import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import bot
import random
import json
import youtube_dl
import os
import giphy_client
import asyncio
import utils
from discord.utils import get
import traceback
import sys
from dotenv import load_dotenv
import time

from webserver import keep_alive
import systems
import settings
import error_handle
# import play_music

CHECK_VERIFY_CHANNEL_ID = 1224997926871236679
VOTE_CHANNEL_ID = 1220993715531677708
DISCORD_API = os.environ['DISCORD_API']

logger = systems.logging.getLogger("bot")


VOTE_FILE = "vote_file.txt"


async def read_votes():
    """Reads vote count from the file."""
    try:
        with open(VOTE_FILE, "r") as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        with open(VOTE_FILE, "w") as f:
            json.dump({}, f)
        return {}


async def update_votes(vote_dict):
    with open(VOTE_FILE, "w") as f:
        json.dump(vote_dict, f)


class formDangKy(discord.ui.Modal, title="Đăng ký"):
    title1 = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Số tài khoản",
        required=False,
        placeholder="Nhập số tài khoản",)
    title2 = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="CTK",
        required=False,
        placeholder="Nhập CTK",)
    title3 = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="ID DISCORD",
        required=False,
        placeholder="Nhập ID",)
    title4 = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Link Facebook cá nhân",
        required=False,
        placeholder="Link Facebook",)
    title5 = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Zalo",
        required=False,
        placeholder="SĐT Zalo",)


class Menu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.value = None
        self.user_id = user_id

    async def send(self, ctx):
        channel = ctx.guild.get_channel(VOTE_CHANNEL_ID)
        self.from_message = await channel.send(view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_vote = await read_votes()
        vote_count = current_vote.get(self.user_id, 0) + 1
        current_vote[self.user_id] = vote_count
        await update_votes(current_vote)
        await interaction.response.edit_message(content=f"Vote: {vote_count}")
        self.value = False
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_votes = await read_votes()
        vote_count = current_votes.get(self.user_id, 0) - 1
        vote_count = max(vote_count, 0)
        current_votes[self.user_id] = vote_count
        await update_votes(current_votes)
        await interaction.response.edit_message(content=f"Vote: {vote_count}")
        self.value = False
        self.stop()

    @discord.ui.button(label="None", style=discord.ButtonStyle.blurple)
    async def menu3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="")
        self.value = False
        self.stop()
# Prefix/setup

    async def on_submit(self, ctx, interaction: discord.Interaction, member: discord.Member = None):
        username = member if member else ctx.author
        title1 = self.title1.value
        title2 = self.title2.value
        title3 = self.title3.value
        title4 = self.title4.value
        title5 = self.title5.value
        embed = discord.Embed(title=f"Thông tin đăng nhập {username}",
                              description=f"1: {title5}")
        await interaction.response.send_message(f"Bạn đã thành công gửi yêu cầu verify tới admin!", ephemeral=True)
        channel = interaction.guild.get_channel(CHECK_VERIFY_CHANNEL_ID)
        await channel.send(embed=embed)
        time.sleep(3)
        await interaction.delete_original_response()


class verification(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # @discord.ui.button(label="Verify", custom_id="Verify", style=discord.ButtonStyle.success)
    # async def verify(self, verify, button):
    #     role = 1224875800961224756
    #     user = verify.user
    #     if role not in [y.id for y in user.roles]:
    #         await user.add_roles(user.guild.get_role(role))
    #         await user.send("Ban da verify thanh cong !")
    #     else:
    #         await user.send("Ban da verify roi !")

    @discord.ui.button(label="Sign in", style=discord.ButtonStyle.grey)
    async def sign_in(self, sign_in, button):
        await sign_in.response.send_modal(formDangKy())


# intents
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

# client
client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command("help")

# Events


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Mua Robux Tại Mazer Store'))
    logger.info(f"User:{client.user} (ID: {client.user.id})")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Câu lệnh sai, gõ 'help' để hiển thị toàn bộ lệnh")
        time.sleep(1)
        await ctx.channel.purge(limit=1)


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name='Unverified')
    await member.add_roles(role)


@client.command()
async def help(ctx):
    help_embed = discord.Embed(
        title="Hướng dẫn sử dụng bot", color=discord.Color.blue())
    help_embed.set_author(name="MAZER BOT")
    help_embed.add_field(name="clear [amout]", value="Xóa tin nhắn")
    help_embed.add_field(name="checkcoc [@user]", value="Check tiền cọc")
    help_embed.add_field(name="vote [@user]", value="Vote uy tín")
    help_embed.add_field(
        name="mazer", value="Hiển thị thông tin cửa hàng Mazer và liên kết cửa hàng.")
    help_embed.add_field(
        name="userinfo [@user]", value="Hiên thị thông tin của người dùng.")
    help_embed.add_field(name="dangky", value="BETA")
    await ctx.send(embed=help_embed)


@client.command()
async def dangky(ctx):
    embed = discord.Embed(
        title="verification", description="(BETA).")
    await ctx.send(embed=embed, view=verification())


@client.command()
async def checkcoc(ctx, user: discord.Member = None):
    """Check tiền cọc."""

    member = user or ctx.author
    member_role = discord.utils.get(ctx.guild.roles, name="Member")

    if member_role in ctx.author.roles:
        for role in user.roles:
            if "Đã cọc" in role.name:
                embed = discord.Embed(
                    colour=member.colour,
                    timestamp=ctx.message.created_at,
                    description=f"Tiền cọc của {member}",
                )
                embed.set_author(name=f"Tổng tiền cọc của {member}")
                embed.add_field(name="Tiền đã cọc",
                                value=f"{member.mention},{role.name}")
                await ctx.author.send(embed=embed)
                return
        else:
            await ctx.author.send(f"{member.mention} chưa cọc")


@client.command(help='Xóa tin nhắn')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)


@ client.command()
async def vote(ctx, member: discord.Member = None):
    """Vote uy tín."""
    global luu_vote
    global vote_complete
    luu_vote = await read_votes()
    vote_complete = 0
    checkgdv_channel = ctx.guild.get_channel(VOTE_CHANNEL_ID)
    view = Menu(ctx.author.id)
    member = member if member else ctx.author
    checkuytin = ""
    # x = thisdict.get("model")
    if str(ctx.author.id) in luu_vote:
        vote_complete = luu_vote.get(str(ctx.author.id))
    if vote_complete == 0:
        checkuytin = "không uy tín"
    else:
        checkuytin = "uy tín"
    roles = [role for role in member.roles]
    embed = discord.Embed(
        colour=member.colour, timestamp=ctx.message.created_at, description=f"Vote {member}")
    embed.set_author(name=f"Duyệt vote - người gửi yêu cầu: {ctx.author}")
    embed.add_field(name="Số vote", value=f"{checkuytin}")
    embed.add_field(name=f"Vai trò ({len(roles)})", value=" ".join(
        [role.mention for role in roles]))
    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Tên hiển thị:", value=member.display_name)
    embed.add_field(name="Ngày tạo:", value=member.created_at.strftime(
        "%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Ngày tham gia:", value=member.joined_at.strftime(
        "%a, %#d %B %Y, %I:%M %p UTC"))
    await ctx.author.send("Đang gửi yêu cầu cho admin")
    await checkgdv_channel.send(embed=embed, view=view)
    time.sleep(0.5)
    await ctx.author.send("Đã gửi")
    await ctx.author.send(f"Tự động xóa để bảo mật thông tin của bạn {ctx.author}")
    await ctx.channel.purge(limit=1)


@client.command(help='Hiện thông tin cá nhân')
async def userinfo(ctx, member: discord.Member = None):
    member = member if member else ctx.author
    roles = [role for role in member.roles]
    embed = discord.Embed(
        colour=member.colour, timestamp=ctx.message.created_at, description=f"Vote {member}")
    embed.set_author(name=f"Thông tin người dùng - {ctx.author}")
    embed.add_field(name="Số vote", value="1")
    embed.add_field(name=f"Vai trò ({len(roles)})", value=" ".join(
        [role.mention for role in roles]))
    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Tên hiển thị:", value=member.display_name)
    embed.add_field(name="Ngày tạo:", value=member.created_at.strftime(
        "%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Ngày tham gia:", value=member.joined_at.strftime(
        "%a, %#d %B %Y, %I:%M %p UTC"))
    await ctx.send(embed=embed)


class ShopLink(discord.ui.View):
    def __init__(self):
        super().__init__()

        button = discord.ui.Button(
            label="Link Shop", style=discord.ButtonStyle.link, url="https://meatrobux.com/")
        self.add_item(button)


@client.command(help="Hiển thị thông tin cửa hàng Mazer và liên kết cửa hàng.")
async def mazer(ctx, member: discord.Member = None):
    view = ShopLink()
    view.add_item(discord.ui.Button(label="Link Checkgdv", style=discord.ButtonStyle.link,
                  url="https://checkgdvmazer.com/post/gioithieu.html"))
    view.add_item(discord.ui.Button(label="Link Youtube", style=discord.ButtonStyle.link,
                  url="https://www.youtube.com/channel/UCZ5uqQvgKIuITgfrPyp9nMA"))
    member = member if member else ctx.author
    embed = discord.Embed(
        colour=member.colour, timestamp=ctx.message.created_at, description="Mazer Store")
    embed = discord.Embed(
        colour=member.colour, timestamp=ctx.message.created_at, description="Mazer Store")

    embed.set_author(name="Mazer Store")
    embed.add_field(name="**Thông tin thanh toán**",
                    value="**BIDV:** 8802092008 CTK: NGUYEN NGO DUC HIEU\n**MOMO:** 0899599536 CTK NGUYEN NGO DUC HIEU\n**TP BANK: 0966960889 CTK: NGO QUYNH NGA **", inline=False)

    await ctx.send(embed=embed, view=view)



keep_alive()
client.run(systems.DISCORD_API, root_logger=True)
