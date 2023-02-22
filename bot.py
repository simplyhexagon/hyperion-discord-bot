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
import platform
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
BOT_VERSION: str = "0.2.3"

# Vars
bot = commands.Bot(command_prefix="$", intents= discord.Intents.all())
global is_os_windows
is_os_windows = False

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
    if(is_os_windows):
        path = f"{os.getcwd()}\\au_temp\\"
    else:
        path = f"{os.getcwd()}/au_temp/"

    await logger(1, f"Path is {path}")

    audiofiles = os.listdir(path)

    for item in audiofiles:
        if(item.endswith('.mp3')):
            removefile = str(os.path.join(path, item))
            await logger(1, f"Removing file: {removefile}")
            os.remove(removefile)

@bot.event
async def on_ready():
    global is_os_windows
    if(platform.system() == "Windows"):
        is_os_windows = True
        await logger(2, "Bot is running on Windows!!!")
    else:
        is_os_windows = False
        await logger(2, "Bot is running on *nix")
    
    if(IS_BOT_DEV):
        await logger(2, "Bot was launched as a test instance")
    else:
        await logger(2, "Bot was launched as a live instance")

    await logger(1, "Sanitising audio folder...")
    await audio_delete()

    await logger(1, f"Logged in as {bot.user}")
    await logger(1, "Setting status")

    # Uncomment if you only want one status message 
    # activity = discord.Game(name="/commands for more info", type=3)

    # Comment these lines if you don't want separate status messages for DEV and PROD
    if(IS_BOT_DEV):
        activity = discord.Game(name="Under development!", type=3)
    else:
        activity = discord.Game(name="/commands", type=3)
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
    """Testing bot availability"""
    await logger(4, f"\"ping\" command was called by {interaction.user.name}#{interaction.user.discriminator}")
    latency = bot.latency * 1000
    latency = round(latency, 0)
    await interaction.response.send_message(f"*Pong!*\n`Current latency is {latency} ms`")
    await logger(1, f"Current ping is {latency}ms")

@bot.tree.command(name="echo")
@app_commands.describe(echo_content = "Content after the \"/echo\" command that gets echoed back")
async def echo(interaction: discord.Interaction, echo_content: str):
    """Echo the content"""
    await interaction.response.send_message(f"`{echo_content}`")

@bot.tree.command(name="about")
async def about(interaction: discord.Interaction):
    """Information about the bot"""
    response: str = f"*Hyperion {BOT_VERSION}*\Created by: hexagon#1337\nUse `/commands` for more info!"
    await logger(4, f"\"about\" command was called by {interaction.user.name}#{interaction.user.discriminator}")
    await interaction.response.send_message(f"{response}")


@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):
    """Join voice channel"""
    if interaction.user.voice.channel is not None:
        voicechannel = interaction.user.voice.channel
        msgchannel = interaction.channel
        await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} called the bot into \"{voicechannel.name}\" voice channel")
        await interaction.response.send_message(f"I am now attempting to join this voice channel: {voicechannel.name}")
        try:
            global voiceclient
            voiceclient = await voicechannel.connect(self_deaf=True)
            await msgchannel.send(f"Successfully joined {voicechannel.name}")
        except Exception as ex:
            await msgchannel.send("An error occured!")
            await logger(3, f"An exception occured: {ex}")
    else:
        await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} tried to invite bot to voice, but user isn't in a voice channel!")
        await interaction.response.send_message("You are not connected to a voice channel!", ephemeral=True)

@bot.tree.command(name="leave")
async def leave(interaction: discord.Interaction):
    """Leave voice channel"""
    try:
        await logger(1, f"Disconnecting voice client")
        vchannel: discord.VoiceChannel = voiceclient.channel
        if vchannel.name == interaction.user.voice.channel.name:
            await voiceclient.disconnect()
            await interaction.response.send_message("Successfully left voice channel!", ephemeral=True)
            await logger(1, "Voice client disconnected")

    except Exception as ex:
        await logger(3, f"An exception occured: {ex}")
        await interaction.response.send_message("An error occured!", ephemeral=True)

@bot.tree.command(name="voicetest")
async def voicetest(interaction: discord.Interaction):
    """For testing voice capabilities"""
    try:
        if interaction.user.voice.channel is not None:
            voicechannel = interaction.user.voice.channel
            msgchannel = interaction.channel
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} called the bot into \"{voicechannel.name}\" voice channel")
            await interaction.response.send_message(f"I am now attempting to join this voice channel: `{voicechannel.name}`")
            try:
                global voiceclient
                voiceclient = await voicechannel.connect(self_deaf=True)
                await msgchannel.send(f"Successfully joined `{voicechannel.name}`")
                
            except Exception as ex:
                await msgchannel.send("An error occured!")
                await logger(3, f"An exception occured: {ex}")

            await msgchannel.send(f"Playing test audio file...")
            sourcefile = FFmpegPCMAudio("bot_test_voice.mp3", executable=ffmpeg_path)
            player = voiceclient.play(sourcefile)
        else:
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} tried to invite bot to voice, but user isn't in a voice channel!")
            await interaction.response.send_message("You are not connected to a voice channel!", ephemeral=True)
    except Exception as ex:
        await interaction.response.send_message(f"An error occured! Most likely you're not in a voice channel!", ephemeral=True)
        await logger(3, f"An exception occured while running the bot\n\t{ex}")


@bot.tree.command(name="play")
@app_commands.describe(url = "YouTube video URL")
async def play(interaction: discord.Interaction, url: str):
    """Music playback from YouTube (only available with URL, no search)"""
    try:
        await interaction.response.send_message("Starting music playback procedure...")
        if interaction.user.voice.channel is not None:
            voicechannel = interaction.user.voice.channel
            msgchannel = interaction.channel
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} called the bot into \"{voicechannel.name}\" voice channel to play media")

            await msgchannel.send(f"I am now attempting to join this voice channel: `{voicechannel.name}`")
            try:
                global voiceclient
                voiceclient = await voicechannel.connect(self_deaf=True)
                await msgchannel.send(f"Successfully joined `{voicechannel.name}`")
                
            except Exception as ex:
                await logger(3, f"An exception occured: {ex}")

            if not voiceclient.is_playing():
                try:
                    if(is_os_windows):
                        pingsourcefile = FFmpegPCMAudio(f".\\wait.mp3", executable=ffmpeg_path)
                    else:
                        pingsourcefile = FFmpegPCMAudio(f"./wait.mp3", executable=ffmpeg_path)

                    await msgchannel.send(f"Loading sound data...")
                    # Generating a random string for destination
                    letters = string.ascii_lowercase
                    outputstring = ''.join(random.choice(letters) for i in range(10))
                    await logger(1, f"Random file path: {outputstring}")

                    if(is_os_windows):
                        command = f"{ytdl_path} {url} -f 251 -x --audio-format mp3 --output .\\au_temp\\{outputstring}.%(ext)s"

                    else:
                        command = f"{ytdl_path} {url} -f 251 -x --audio-format mp3 --output ./au_temp/{outputstring}.%(ext)s"

                    await logger(1, f"Bot is currently waiting for this to complete:\n{command}")        
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                    while (process.poll() != 0):
                        time.sleep(3)
                        await logger(1, "Still waiting for process to finish...")
                        player = voiceclient.play(pingsourcefile)

                    if voiceclient.is_playing():
                        voiceclient.stop()

                        if(is_os_windows):
                            sourcefile = FFmpegPCMAudio(f".\\au_temp\\{outputstring}.mp3", executable=ffmpeg_path)
                        else:
                            sourcefile = FFmpegPCMAudio(f"./au_temp/{outputstring}.mp3", executable=ffmpeg_path)

                        await logger(1, f"Starting playback in voice channel {voiceclient.channel.name}")
                        await msgchannel.send("Starting playback...")
                        player = voiceclient.play(sourcefile) 

                except Exception as ex:
                    await msgchannel.send("An error occured!")
                    await logger(3, f"An exception occured: {ex}")

            elif voiceclient.is_playing():
                await msgchannel.send("I am already playing an audio file!")

        else:
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} tried to invite bot to voice, but user isn't in a voice channel!")
            await msgchannel.send("You are not connected to a voice channel!")
    except Exception as ex:
        await interaction.response.send_message(f"An error occured! Most likely you're not in a voice channel!", ephemeral=True)
        await logger(3, f"An exception occured while running the bot\n\t{ex}")
                

@bot.tree.command(name="stop")
async def stop(interaction: discord.Interaction):
    """Stop current music playback"""
    try:
        await logger(1, f"Stopping music playback")
        vclients = bot.voice_clients
        for vclient in vclients:
            vchannel: discord.VoiceChannel = vclient.channel
            if vchannel.name == interaction.user.voice.channel.name:
                vclient.stop()
                await interaction.response.send_message("Playback stopped!", ephemeral=True)
                await logger(1, "Voice client stopped playback")

    except Exception as ex:
        await logger(3, f"An exception occured: {ex}")
        await interaction.response.send_message("An error occured!", ephemeral=True)


@bot.tree.command(name="commands")
async def commands(interaction: discord.Interaction):
    """List of commands"""
    await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} called `/commands`")
    response: str = f'''
    `/commands`: List of commands
    `/ping`: Test bot availability
    `/echo <message>`: Echo the message back
    `/about`: Information about the bot
    `/join`: Join your voice channel
    `/leave`: Leave your voice channel
    `/voicetest`: Test voice capabilities
    `/play <YouTube URL>`: Audio playback from YouTube
    `/stop`: Stop playback
    '''
    await interaction.response.send_message(f"Available commands: \n{response}")



######### Admin only commands #########

# Use the role names of your own server here
adminRoleNames = ["Captain", "Command Crew"]

# This function is only for checking if the target is an admin
async def isUserAdmin(user: discord.Member):
    userIsAdmin: bool = False
    for item in adminRoleNames:
        role = discord.utils.find(lambda r: r.name == item, user.guild.roles)
        if role in user.roles:
            userIsAdmin = True

    return userIsAdmin
# Admin check END

# This function is only for checking if the command's user is an admin
async def isUserAdmin(user: discord.Interaction.user):
    userIsAdmin: bool = False
    for item in adminRoleNames:
        role = discord.utils.find(lambda r: r.name == item, user.guild.roles)
        if role in user.roles:
            userIsAdmin = True

    return userIsAdmin
# Admin check END


@bot.tree.command(name="dm")
async def dm(interaction: discord.Interaction, user: discord.Member, message: str):
    """Send a test DM to the selected user"""
    await logger(1, f"User {interaction.user.name}#{interaction.user.discriminator} wants to send a DM to {user.name}#{user.discriminator} through the bot")
    sender = interaction.user
    if(await isUserAdmin(sender)):
        # Proceed
        await logger(4, f"Message contents are as follows:\n\t{message}")
        target = await bot.fetch_user(user.id)
        if(await target.send(message)):
            await interaction.response.send_message(f"Message sent!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Failed to deliver message!", ephemeral=True)
    else:
        await interaction.response.send_message(f"You don't have the rights!", ephemeral=True)
    

#######################################

if(IS_BOT_DEV):
    # Log in as test instance
    bot.run(dev_token)
else:
    # Log in as live instance
    bot.run(prod_token)