import os
from dotenv import load_dotenv
import cairo

import discord
from discord.ext import commands

from main import generate_image_bytes


# --------------------
# setup
# --------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

prefix = "!"
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix=prefix, intents=intents)


# --------------------
# bot config (optimised for kanji)
# --------------------
config = {
    # font
    "FONT": ("Noto Sans JP", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
    "FONT_SIZE": 100,
    "STROKE_WIDTH": 2,
    "STROKE_COLOR": (0, 0, 0),
    "FILL_COLOR": (1, 0.65, 0),

    # misc
    "PADDING": 5,

    # fire
    "FIRE_PADDING": 0.6,
    "FIRE_DECR_CHANCE": 0.2,
    "FIRE_DRAW_IDX_MIN": 4,
    "FIRE_GRID_HEIGHT": 157,
    "FIRE_GRID_WIDTH": 90
}


# --------------------
# functions
# --------------------
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.command()
async def make(ctx, text: str):
    img_data = generate_image_bytes(text, config)
    await ctx.send(file=discord.File(img_data, filename="image.png"))


client.run(TOKEN)
