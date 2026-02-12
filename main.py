import discord
from discord.ext import commands
import os
import re

# CONFIG
CUSTOMER_ROLE_ID = 1446629248491327550
ADMIN_ROLE_IDS = [1446628032541491384]

TOKEN = os.getenv("TOKEN")

# BOT SETUP
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
    await bot.tree.sync()
    print(f"Bot online as {bot.user}!")

# =====================================
#              COMMANDS
# =====================================

# HELP
@bot.tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help",
        description="Commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/calc <expr>", value="Calculates expressions like 5m+2k", inline=False)
    embed.add_field(name="/acalc <expr>", value="Calculates and outputs /pay <IGN> <amount>", inline=False)
    embed.add_field(name="/percent <percent> <amount>", value="Calculate percent of an amount", inline=False)
    embed.add_field(name="/ign <username>", value="Set your IGN", inline=False)
    embed.add_field(name="/roleadd @user", value="Add customer role (admin only)", inline=False)
    embed.add_field(name="/roleremove @user", value="Remove customer role (admin only)", inline=False)

    await interaction.response.send_message(embed=embed)

# IGN
@bot.tree.command(name="ign", description="Set your IGN")
async def ign(interaction: discord.Interaction, ign_name: str):
    igns[interaction.user.id] = ign_name

    embed = discord.Embed(
        title="IGN Set",
        description=f"Your IGN is now: `{ign_name}`",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# CALC
@bot.tree.command(name="calc", description="Calculate expressions like 5m+2k")
async def calc(interaction: discord.Interaction, expression: str):
    try:
        total = calculate_expression(expression)
    except Exception:
        await interaction.response.send_message("Invalid expression!")
        return

    embed = discord.Embed(
        title="Result",
        description=f"{total:,}",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ACALC
@bot.tree.command(name="acalc", description="Calculate and output /pay <IGN> <amount>")
async def acalc(interaction: discord.Interaction, expression: str):
    user_ign = igns.get(interaction.user.id)

    if not user_ign:
        await interaction.response.send_message(
            "Set your IGN first with /ign <username>",
            ephemeral=True
        )
        return

    try:
        total = calculate_expression(expression)
    except Exception:
        await interaction.response.send_message("Invalid expression!")
        return

    embed = discord.Embed(
        title="ACalc Result",
        description=f"/pay {user_ign} {total}",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# PERCENT
@bot.tree.command(name="percent", description="Calculate percent of an amount")
async def percent(interaction: discord.Interaction, percent_value: float, amount: str):
    try:
        amount_value = parse_number(amount)
    except:
        await interaction.response.send_message(
            "Invalid amount format! Use 10m or 5b etc.",
            ephemeral=True
        )
        return

    result = amount_value * (percent_value / 100)

    embed = discord.Embed(
        title="Percent Calculator",
        description=f"**{percent_value}%** of **{amount_value:,}** = **{result:,}**",
        color=discord.Color.purple()
    )

    await interaction.response.send_message(embed=embed)

# ROLE ADD
@bot.tree.command(name="roleadd", description="Add customer role (admin only)")
async def roleadd(interaction: discord.Interaction, member: discord.Member):

    if not any(role.id in ADMIN_ROLE_IDS for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return

    role = interaction.guild.get_role(CUSTOMER_ROLE_ID)

    if not role:
        await interaction.response.send_message("Customer role not found.", ephemeral=True)
        return

    await member.add_roles(role)

    embed = discord.Embed(
        title="Role Added",
        description=f"Added `{role.name}` to {member.display_name}",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ROLE REMOVE
@bot.tree.command(name="roleremove", description="Remove customer role (admin only)")
async def roleremove(interaction: discord.Interaction, member: discord.Member):

    if not any(role.id in ADMIN_ROLE_IDS for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return

    role = interaction.guild.get_role(CUSTOMER_ROLE_ID)

    if not role:
        await interaction.response.send_message("Customer role not found.", ephemeral=True)
        return

    await member.remove_roles(role)

    embed = discord.Embed(
        title="Role Removed",
        description=f"Removed `{role.name}` from {member.display_name}",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)

# RUN BOT
bot.run(TOKEN)
