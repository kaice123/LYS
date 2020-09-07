import discord
import asyncio
import datetime
from datetime import datetime
import json
from random import *
from discord.ext import commands
import youtube_dl
import urllib
import os
import traceback
import ffmpeg
from requests import post

client = commands.Bot(command_prefix='릿 ')
#안된다
client.remove_command("help")

for filename in os.listdir("C:\\bot\\Cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"Cogs.{filename[:-3]}")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name='놀쟈아'))
    #온라인 online 자리비움 idle 방해금지 do_not_disturb, dnd
    print(f'히힛~!')

token = ("NzI4ODY3MDAzODk2NTYxNzM1.XwFGhQ.5keZrM8GbsuNZoHpKFRixVBsRMQ")

client.run(token, reconnect=True) #리스 귀여움 >.< #이제 그럼 된거네

