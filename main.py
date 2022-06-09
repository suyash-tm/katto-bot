import json
import os
import platform
import sys
import traceback
import motor.motor_asyncio
from pathlib import Path
import logging
import collections
import datetime
import nextcord
from nextcord.ext import commands
import utility
from utility.mongo import *

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

intents = nextcord.Intents.all()


async def get_prefix(bot, message):
    # If dm's 
    if not message.guild:
        return commands.when_mentioned_or("!")(bot, message)
    try:
        data = await bot.config.find(message.guild.id)

    # Make sure we have a use-able prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(".")(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(".")(bot, message)


bot = commands.Bot(command_prefix=get_prefix,case_insensitive=True,strip_after_prefix=True,owner_id=967784061382832148,help_command=None,intents=intents)
bot.connection_url = config["mongoDB"]


@bot.event
async def on_ready() -> None:
    print("-------------------")
    print(f"Logged in as {bot.user.name}")
    print(f"Nextcord API version: {nextcord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    # Mongo DataBase
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["menudocs"]
    bot.config = Document(bot.db, "config")
    print("Initialized Database")
    for document in await bot.config.get_all():
      #remove this later to avoid terminal clutter
      print(document)

@bot.event
async def on_connect():
  await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=".help | katto.gg"))

# Fix this shit later
@bot.event
async def on_message(message):
  # Whenever the bot is tagged, respond with its prefix
  if message.author.bot == False and bot.user.mentioned_in(message) and len(message.content) == len(bot.user.mention):
      data = await bot.config.get_by_id(message.guild.id)
      if not data or "prefix" not in data:
        prefix = "."
      else:
        prefix = config["prefix"]
        await message.channel.send(f"Prefix for this server is `{prefix}`**")

  await bot.process_commands(message)



extensions= [
    "",
    "",
  ]
if __name__=="__main__":
  for extension in extensions:
    try:
      bot.load_extension(extension)
    except Exception as e:
      print(f"Error while loading{extension}",file=sys.stderr)
      traceback.print_exc()

bot.run(config["token"])
