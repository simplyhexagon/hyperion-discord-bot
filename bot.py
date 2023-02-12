# Imports
import discord
from discord import app_commands
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio

import logging
import datetime
import nacl

import json
import os
import time
import string
import random
import subprocess

#!SECTION Checking if config file exists
if os.path.exists("./config.json"):
    with open("./config.json") as config:
        configData = json.load(config)
        dev_token = configData["DEV_TOKEN"]
        prod_token = configData["PROD_TOKEN"]
        ffmpeg_path = configData["FFMPEG_PATH"]
        ytdl_path = configData["YTDL_PATH"]
else:
    print("config.json does not exist in the current directory!")
    configTemplate = {"PROD_TOKEN": "", "DEV_TOKEN": "", "FFMPEG_PATH": "", "YTDL_PATH": ""}

    with open("./config.json", "w+") as f:
        json.dump(configTemplate, f)
        print("created config template")
        print("\nPlease fill in the tokens in your config.json and restart the bot!")
        exit()

# Constants
IS_BOT_DEV = True
BOT_VERSION: str = "0.1.0"

# Vars
#intents_ = discord.Intents.all()
#intents_.message_content = True

# client = discord.Client(intents=intents_)
bot = commands.Bot(command_prefix="$", intents= discord.Intents.all())

# Setting up log file
log = logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.DEBUG)

async def logger(level, message):
    now = datetime.datetime.now()
    output = ""
    output = output + now.strftime("%Y-%m-%d %H:%M:%S | ")
    if(level == 1):
        logging.info(output + message)
        output = output + "[INFO]\t"
        output = output + message
        
    if(level == 2):
        logging.warning(output + message)
        output = output + "[WARN]\t"
        output = output + message
        
    if(level == 3):
        logging.error(output + message)
        output = output + "[FAIL]\t"
        output = output + message
        
    if(level == 4):
        logging.debug(output + message)
        output = output + "[MSG]\t"
        output = output + message
        
    print(output)

async def audio_delete():
    path = f"{os.getcwd()}\\au_temp\\"
    for file_name in os.listdir(path):
        # construct full file path
        file = path + file_name
        if os.path.isfile(file):
            await logger(1, f'Deleting file: {file}')
            os.remove(file)

@bot.event
async def on_ready():
    if(IS_BOT_DEV):
        await logger(2, "Bot was launched as a test instance")
    else:
        await logger(2, "Bot was launched as a live instance")

    await logger(1, "Sanitising audio folder...")
    await audio_delete()

    await logger(1, f"Logged in as {bot.user}")
    await logger(1, "Setting status")
    activity = discord.Game(name="Parancsok: /commands", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

    try:
        synced = await bot.tree.sync()
        await logger(1, f"Synced {len(synced)} command(s)")
    except Exception as e:
        await logger(3, f"Exception occured! {e}")

    await logger(1, "Discord bot ready")


# Slash commands
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    """Bot elérhetőségének tesztelése"""
    await logger(4, f"\"ping\" command was called by {interaction.user.name}")
    await interaction.response.send_message(f"*Pong!*")

@bot.tree.command(name="echo")
@app_commands.describe(echo_content = "A tartalom az \"/echo\" parancs után, amit visszaküldök")
async def echo(interaction: discord.Interaction, echo_content: str):
    """Az `echo_content` visszaírása egy kis plusszal"""
    await interaction.response.send_message(f"{interaction.user.mention} ezt mondja:\n`{echo_content}`")

@bot.tree.command(name="about")
async def about(interaction: discord.Interaction):
    """Információ a botról"""
    response: str = f"*Hyperion {BOT_VERSION}*\nKészítette: hexagon#1337\nTovábbi információért írd be a `/commands` parancsot!"
    await logger(4, f"\"about\" command was called by {interaction.user.name}")
    await interaction.response.send_message(f"{response}")


@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):
    """Csatlakozás hangos csevegőszobához"""
    if interaction.user.voice.channel is not None:
        voicechannel = interaction.user.voice.channel
        msgchannel = interaction.channel
        await logger(1, f"{interaction.user.name} called the bot into \"{voicechannel.name}\" voice channel")
        await interaction.response.send_message(f"Megpróbálok csatlakozni ehhez a hangos csevegőszobához: {voicechannel.name}")
        try:
            global voiceclient
            voiceclient = await voicechannel.connect(self_deaf=True)
            await msgchannel.send(f"Sikeresen csatlakoztam ide: {voicechannel.name}")
        except Exception as ex:
            await msgchannel.send("Hiba történt a bot futása során!")
            await logger(3, f"An exception occured: {ex}")
    else:
        await logger(1, f"{interaction.user.name} tried to invite bot to voice, but user isn't in a voice channel!")
        await interaction.response.send_message("Nem vagy csatlakozva hangos csevegőszobához!", ephemeral=True)

@bot.tree.command(name="leave")
async def leave(interaction: discord.Interaction):
    """Hangos csevegőszoba elhagyása"""
    try:
        await logger(1, f"Disconnecting voice client")
        vchannel: discord.VoiceChannel = voiceclient.channel
        if vchannel.name == interaction.user.voice.channel.name:
            await voiceclient.disconnect()
            await interaction.response.send_message("Sikeresen elhagytam a szobát!", ephemeral=True)
            await logger(1, "Voice client disconnected")

    except Exception as ex:
        await logger(3, f"An exception occured: {ex}")
        await interaction.response.send_message("Hiba történt a bot futása során!", ephemeral=True)

@bot.tree.command(name="voicetest")
async def voicetest(interaction: discord.Interaction):
    """\"Beszéd\" használatának tesztelése"""
    if interaction.user.voice.channel is not None:
        voicechannel = interaction.user.voice.channel
        msgchannel = interaction.channel
        await logger(1, f"{interaction.user.name} called the bot into \"{voicechannel.name}\" voice channel")
        await interaction.response.send_message(f"Megpróbálok csatlakozni ehhez a hangos csevegőszobához: `{voicechannel.name}`")
        try:
            global voiceclient
            voiceclient = await voicechannel.connect(self_deaf=True)
            await msgchannel.send(f"Sikeresen csatlakoztam ide: `{voicechannel.name}`")
            
        except Exception as ex:
            await msgchannel.send("Hiba történt a bot futása során!")
            await logger(3, f"An exception occured: {ex}")

        await msgchannel.send(f"Tesztfájl lejátszása...")
        sourcefile = FFmpegPCMAudio("bot_test_voice.mp3", executable=ffmpeg_path)
        player = voiceclient.play(sourcefile)
    else:
        await logger(1, f"{interaction.user.name} tried to invite bot to voice, but user isn't in a voice channel!")
        await interaction.response.send_message("Nem vagy csatlakozva hangos csevegőszobához!", ephemeral=True)


@bot.tree.command(name="play")
@app_commands.describe(url = "YouTube videó URL-je")
async def play(interaction: discord.Interaction, url: str):
    """Zene lejátszása YouTube-ról (egyelőre link alapján)"""
    await interaction.response.send_message("Zenelejátszási folyamat indítása")
    queuelist = list(())
    if interaction.user.voice.channel is not None:
        voicechannel = interaction.user.voice.channel
        msgchannel = interaction.channel
        await logger(1, f"{interaction.user.name} called the bot into \"{voicechannel.name}\" voice channel to play media")
        try:
            await msgchannel.send(f"Hanganyag letöltése...")
            # Generating a random string for destination
            letters = string.ascii_lowercase
            outputstring = ''.join(random.choice(letters) for i in range(10))
            await logger(1, f"Random file path: {outputstring}")

            command = f"{os.getcwd()}\\{ytdl_path} {url} -f 251 -x --audio-format mp3 --output {os.getcwd()}\\au_temp\{outputstring}.%(ext)s"
            await logger(1, f"Bot is currently waiting for this to complete:\n{command}")
            #os.system(command=command)            
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            while process.wait():
                time.sleep(0.1)

            await msgchannel.send(f"Megpróbálok csatlakozni ehhez a hangos csevegőszobához: `{voicechannel.name}`")
            try:
                global voiceclient
                voiceclient = await voicechannel.connect(self_deaf=True)
                
            except Exception as ex:
                await logger(3, f"An exception occured: {ex}")

            if not voiceclient.is_playing():
                await msgchannel.send(f"Sikeresen csatlakoztam ide: `{voicechannel.name}`")
                sourcefile = FFmpegPCMAudio(f"./au_temp/{outputstring}.mp3", executable=ffmpeg_path)
                player = voiceclient.play(sourcefile)
            
            elif voiceclient.is_playing():
                queuelist.append(url)
                await msgchannel.send("Kért zene várólistához adva")

            
        except Exception as ex:
            await msgchannel.send("Hiba történt a bot futása során!")
            await logger(3, f"An exception occured: {ex}")
    else:
        await logger(1, f"{interaction.user.name} tried to invite bot to voice, but user isn't in a voice channel!")
        await msgchannel.send("Nem vagy csatlakozva hangos csevegőszobához!")

@bot.tree.command(name="stop")
async def stop(interaction: discord.Interaction):
    """Jelenleg lejátszás alatt levő zene leállítása"""
    try:
        await logger(1, f"Stopping music playback")
        vclients = bot.voice_clients
        for vclient in vclients:
            vchannel: discord.VoiceChannel = vclient.channel
            if vchannel.name == interaction.user.voice.channel.name:
                vclient.stop()
                await interaction.response.send_message("Visszajátszás sikeresen leállítva!", ephemeral=True)
                await logger(1, "Voice client disconnected")

    except Exception as ex:
        await logger(3, f"An exception occured: {ex}")
        await interaction.response.send_message("Hiba történt a bot futása során!", ephemeral=True)


@bot.tree.command(name="commands")
async def commands(interaction: discord.Interaction):
    """Parancsok listája"""
    response: str = f'''
    `/commands`: Parancsok listája
    `/ping`: Bot elérhetőségének tesztelése
    `/echo <üzenet>`: Az üzenet visszaírása egy kis plusszal
    `/about`: Információ a botról
    `/join`: Csatlakozás hangos csevegőszobához
    `/leave`: Hangos csevegőszoba elhagyása
    `/voicetest`: \"Beszéd\" használatának tesztelése
    `/play <YouTube Link>`: hang lejátszása YouTube-ról
    `/stop`: Lejátszás megállítása
    '''
    await interaction.response.send_message(f"Elérhető parancsok: \n{response}")

if(IS_BOT_DEV):
    # Hyperion Teszt példány
    bot.run(dev_token)
else:
    # Hyperion Éles
    bot.run(prod_token)