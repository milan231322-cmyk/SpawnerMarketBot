# bot.py
import discord
from discord.ext import commands
import json
import hmac
import hashlib
import os
import random
import string

TOKEN = "YOUR_BOT_TOKEN_HERE"
SECRET_KEY = b"super_secret_hmac_key"  # change to a long random string
KEYS_FILE = "keys.json"

# Load keys
if os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "r") as f:
        KEYS = json.load(f)
else:
    KEYS = {}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== HELPERS =====
def save_keys():
    with open(KEYS_FILE, "w") as f:
        json.dump(KEYS, f, indent=4)

def sign_response(response_dict):
    msg_bytes = json.dumps(response_dict, sort_keys=True).encode()
    sig = hmac.new(SECRET_KEY, msg_bytes, hashlib.sha256).hexdigest()
    return sig

def generate_random_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

# ===== VERIFY COMMAND =====
@bot.slash_command(name="verify", description="Verify your license key")
async def verify(ctx, key: str):
    user_id = str(ctx.author.id)
    response = {"valid": False}

    if key in KEYS and KEYS[key]["valid"]:
        if KEYS[key]["hwid"] is None or KEYS[key]["hwid"] == user_id:
            KEYS[key]["hwid"] = user_id
            response["valid"] = True
        else:
            response["valid"] = False
        save_keys()
    
    sig = sign_response(response)
    embed = discord.Embed(
        title="License Verification",
        color=0x00ff00 if response["valid"] else 0xff0000
    )
    embed.add_field(name="Result", value="✅ Valid" if response["valid"] else "❌ Invalid or used")
    embed.add_field(name="Signature", value=sig)
    await ctx.respond(embed=embed)

# ===== GENERATE COMMAND (ADMIN ONLY) =====
@bot.slash_command(name="generate", description="Generate a new license key (Admin)")
async def generate(ctx, length: int = 12):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You are not an admin!")
        return
    new_key = generate_random_key(length)
    KEYS[new_key] = {"valid": True, "hwid": None}
    save_keys()
    await ctx.respond(f"✅ New key generated: `{new_key}`")

# ===== INVALIDATE COMMAND (ADMIN ONLY) =====
@bot.slash_command(name="invalidate", description="Invalidate a license key (Admin)")
async def invalidate(ctx, key: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You are not an admin!")
        return
    if key in KEYS:
        KEYS[key]["valid"] = False
        save_keys()
        await ctx.respond(f"✅ Key `{key}` invalidated")
    else:
        await ctx.respond(f"❌ Key `{key}` not found")

bot.run(TOKEN)
