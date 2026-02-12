import discord
from discord.ext import commands
import os
import re

# CONFIG
COMMAND_PREFIX = "!"
CUSTOMER_ROLE_ID = 1446629248491327550
ADMIN_ROLE_IDS = [1446628032541491384]

TOKEN = os.getenv("TOKEN")  # Must be set in Railway environment variables

# BOT SETUP
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, help_command=None, intents=intents)

# USER DATA
igns = {}

# UTILITIES
def parse_number(value: str):
    value = value.lower().replace(",", "").strip()
    if value.endswith("k"):
        return int(float(value[:-1]) * 1_000)
    elif value.endswith("m"):
        return int(float(value[:-1]) * 1_000_000)
    elif value.endswith("b"):
        return int(float(value[:-1]) * 1_000_000_000)
    else:
        return int(value)

def calculate_expression(expr: str):
    def replacer(match):
        return str(parse_number(match.group(0)))
    expr = re.sub(r"\d+(\.\d+)?[kKmMbB]", replacer, expr)
    return int(eval(expr))


# EVENTS
@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}!")


# COMMANDS
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!calc <expr>", value="Calculates expressions like 5m+2k", inline=False)
    embed.add_field(name="!acalc <expr>", value="Calculates and outputs /pay <IGN> <amount>", inline=False)
    embed.add_field(name="!percent <percent> <amount>", value="Calculate percent of an amount, e.g. !percent 2 50m", inline=False)
    embed.add_field(name="!ign <username>", value="Set your IGN", inline=False)
    embed.add_field(name="!roleadd customer @user", value="Add customer role (admin only)", inline=False)
    embed.add_field(name="!roleremove customer @user", value="Remove customer role (admin only)", inline=False)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def ign(ctx, *, ign_name):
    igns[ctx.author.id] = ign_name
    embed = discord.Embed(
        title="IGN Set",
        description=f"Your IGN is now: `{ign_name}`",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def calc(ctx, *, expression):
    try:
        total = calculate_expression(expression)
    except Exception:
        await ctx.reply("Invalid expression!", mention_author=False)
        return
    embed = discord.Embed(
        title="Result",
        description=f"{total:,}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def acalc(ctx, *, expression):
    user_ign = igns.get(ctx.author.id)
    if not user_ign:
        await ctx.reply("Set your IGN first with !ign <username>", mention_author=False)
        return
    try:
        total = calculate_expression(expression)
    except Exception:
        await ctx.reply("Invalid expression!", mention_author=False)
        return
    embed = discord.Embed(
        title="ACalc Result",
        description=f"/pay {user_ign} {total:}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)


# =====================================
#         NEW PERCENT COMMAND
# =====================================
@bot.command()
async def percent(ctx, percent_value: float, amount: str):
    """Calculate percent of amount. Example: !percent 2 500m"""

    try:
        amount_value = parse_number(amount)
    except:
        await ctx.reply("Invalid amount format! Use 10m or 5b etc.", mention_author=False)
        return

    result = amount_value * (percent_value / 100)

    embed = discord.Embed(
        title="Percent Calculator",
        description=f"**{percent_value}%** of **{amount_value:,}** = **{result:,}**",
        color=discord.Color.purple()
    )

    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def roleadd(ctx, member: discord.Member = None):
    if ctx.author.id not in ADMIN_ROLE_IDS:
        await ctx.reply("You do not have permission.", mention_author=False)
        return
    if not member:
        await ctx.reply("Mention a user.", mention_author=False)
        return
    role = ctx.guild.get_role(CUSTOMER_ROLE_ID)
    if not role:
        await ctx.reply("Customer role not found.", mention_author=False)
        return
    await member.add_roles(role)
    embed = discord.Embed(
        title="Role Added",
        description=f"Added `{role.name}` to {member.display_name}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def roleremove(ctx, member: discord.Member = None):
    if ctx.author.id not in ADMIN_ROLE_IDS:
        await ctx.reply("You do not have permission.", mention_author=False)
        return
    if not member:
        await ctx.reply("Mention a user.", mention_author=False)
        return
    role = ctx.guild.get_role(CUSTOMER_ROLE_ID)
    if not role:
        await ctx.reply("Customer role not found.", mention_author=False)
        return
    await member.remove_roles(role)
    embed = discord.Embed(
        title="Role Removed",
        description=f"Removed `{role.name}` from {member.display_name}",
        color=discord.Color.red()
    )
    await ctx.reply(embed=embed, mention_author=False)


# RUN BOT
bot.run(TOKEN)

