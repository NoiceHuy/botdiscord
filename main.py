
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
logger = systems.logging.getLogger("bot")

user_id = None
VOTE_CHANNEL_ID = 1220993715531677708
VOTE_FILE = "vote_file.txt"
CHECK_VERIFY_CHANNEL_ID = 1224997926871236679

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

# client
client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command("help")

class MenuVote(discord.ui.View):
    def __init__(self, member : discord.Member = None):
        self.member = member_tag.id
        super().__init__()
        self.value = None


    @discord.ui.button(label = 'Accept', style = discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member_tag = self.member
        get_member_tag = await get_vote_data()
        get_member_tag[str(member_tag)]["Vouch"] += 1
        with open("vote_save_data.json", "w") as f:
            json.dump(get_member_tag,f)
        await interaction.response.send_message(f"Đã + 1 vote cho {member_tag}")
        self.value = False
        self.stop()

    @discord.ui.button(label = 'Deciline', style = discord.ButtonStyle.danger)
    async def deciline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member_tag = self.member
        get_member_tag = await get_vote_data()
        get_member_tag[str(member_tag)]["Vouch"] -= 1
        with open("vote_save_data.json", "w") as f:
            json.dump(get_member_tag,f)
        await interaction.response.send_message(f"Đã - 1 vote cho {member_tag}")
        self.value = False
        self.stop()

    @discord.ui.button(label = 'None', style = discord.ButtonStyle.blurple)
    async def none_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
# Prefix/setup


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

    async def on_submit(self, interaction: discord.Interaction):
        user = client.get_user(user_id)
        send_channel = CHECK_VERIFY_CHANNEL_ID
        title1 = self.title1.value
        title2 = self.title2.value
        title3 = self.title3.value
        title4 = self.title4.value
        title5 = self.title5.value
        embed = discord.Embed(title=f"Thông tin đăng nhập - {user.mention}",
                              description=f"Số tài khoản: {title1}\nCTK: {title2}\nID DISCORD: {title3}\nLink Facebook cá nhân: {title4}\nZalo: {title5}", color=0x00ff00)
        await interaction.response.send_message(f"Bạn đã thành công gửi yêu cầu verify tới admin!", ephemeral=True)
        channel = interaction.guild.get_channel(CHECK_VERIFY_CHANNEL_ID)
        await channel.send(embed=embed, view=Menu_Form())
        time.sleep(3)
        await interaction.delete_original_response()


class Menu_Form(discord.ui.View):
    def __init__(self, member: discord.Member = None):
        super().__init__(timeout=None)

        self.member = member
        self.value = True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.member = interaction.guild.get_member(user_id)
        if self.value:
            verify_role = discord.utils.get(
                interaction.guild.roles, name="Member")
            if verify_role:
                await self.member.add_roles(verify_role)
                await interaction.response.send_message(f"Đã xác minh người dùng {self.member}.")
                self.value = False
                self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()


class verification(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Đăng ký", style=discord.ButtonStyle.grey)
    async def sign_in(self, sign_in, button):
        global user_id
        user_id = sign_in.user.id
        await sign_in.response.send_modal(formDangKy())


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

# commands


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
    help_embed.add_field(
        name="verify", value="Để gửi form verify tới admin")
    await ctx.send(embed=help_embed)


@client.command()
async def verify(ctx, member: discord.Member = None):
    global user_id
    user = member if member else ctx.author
    user_id = user.id

    embed = discord.Embed(
        title="Đăng ký", description="Hướng dẫn Verify.")
    embed.add_field(
        name="Thông tin sẽ được xác nhận trong vòng 24h.", value="```- Mọi người điền đầy đủ thông tin, stk / CTK / id discord / link facebook / zalo / lưu ý 1 thông tin chỉ được vào một lần\n- Có thể dms support hoặc gửi thông tin vào chat để hỗ trợ\n- Điền thông tin chính xác và đầy đủ nếu điền sai sẽ không thành Member ```")

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

async def open_vote_data(member_tag):
    get_member_tag = await get_vote_data()
    if str(member_tag.id) in get_member_tag:
        return False
    else:
        get_member_tag[str(member_tag.id)] = {"Vouch": 0}
    print("get member in data",get_member_tag)
    with open("vote_save_data.json", "w") as f:
        json.dump(get_member_tag,f)
    return True

async def get_vote_data():
    with open("vote_save_data.json", "r") as f:
        get_member_tag = json.load(f)
    print("Get vote data: ", get_member_tag)
    return get_member_tag

@client.command()
async def vote(ctx, member: discord.Member = None):
    """Vote uy tín."""
    roles = [role for role in member.roles]
    checkgdv_channel = ctx.guild.get_channel(VOTE_CHANNEL_ID)
    print(ctx.author)
    global member_tag
    member_tag = member
    if member_tag == None:
        await ctx.send("Bạn đã nhập thiếu giá trị @[user]")
        await ctx.channel.purge(limit=1)
    elif member_tag == ctx.author:
        await ctx.send("Bạn không được tự vote chính mình")
        await ctx.channel.purge(limit=1)
    else:
        await open_vote_data(member_tag)
        print("command vote member_tag",member_tag)
        get_member_tag = await get_vote_data()

        vote_count = get_member_tag[str(member_tag.id)]["Vouch"]

        embed = discord.Embed(title = f"Vote {member_tag}",timestamp=ctx.message.created_at, color = discord.Color.blurple())
        embed.set_author(name=f"Duyệt vote - người gửi yêu cầu: {ctx.author}")
        embed.add_field(name="Số vote", value = f"{vote_count}")
        embed.add_field(name=f"Vai trò ({len(roles)})", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Tên hiển thị:", value=member.display_name)
        embed.add_field(name="Ngày tạo:", value=member.created_at.strftime(
            "%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Ngày tham gia:", value=member.joined_at.strftime(
            "%a, %#d %B %Y, %I:%M %p UTC"))
        await ctx.author.send("Đang gửi yêu cầu cho admin")
        await checkgdv_channel.send(embed=embed, view=MenuVote(member_tag))
        time.sleep(0.5)
        await ctx.author.send("Đã gửi")
        await ctx.author.send(f"Tự động xóa để bảo mật thông tin của bạn {ctx.author}")
        await ctx.channel.purge(limit=1)


@client.command(help='Hiện thông tin cá nhân')
async def userinfo(ctx, member: discord.Member = None):
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
    member = member if member else ctx.author
    roles = [role for role in member.roles]
    embed = discord.Embed(
        colour=member.colour, timestamp=ctx.message.created_at, description=f"Vote {member}")
    embed.set_author(name=f"Thông tin người dùng - {ctx.author}")
    embed.add_field(name="Số vote", value=f"{checkuytin}")
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
