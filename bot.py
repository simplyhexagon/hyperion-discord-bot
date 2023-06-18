#!/bin/python
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
import threading

import sqlite3

# For moderation
import re

# Constants
IS_BOT_DEV = True
BOT_VERSION: str = "0.5-2"

CONFIG_PATH: str = "./configs/config.json"
TOKEN_PATH: str = "./configs/token.json"
BADWORDS_PATH: str = "./configs/badwords.json"

# Vars
global is_os_windows
is_os_windows = False
global database

global badWordsDict
badWordsDict = []

# Setting up log file
log = logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.DEBUG)

logo: str = """  _   _                       _             
 | | | |_   _ _ __   ___ _ __(_) ___  _ __  
 | |_| | | | | '_ \ / _ \ '__| |/ _ \| '_ \ 
 |  _  | |_| | |_) |  __/ |  | | (_) | | | |
 |_| |_|\__, | .__/ \___|_|  |_|\___/|_| |_|
        |___/|_|                            """

output:str = f"Hyperion Discord Bot {BOT_VERSION}, developed by simplyhexagon\n\n{logo}\n\n"
logging.info(f"Starting Hyperion...\n\n\n{output}")
print(f"\n{output}")

logging.info("Loading...\n")
print("Loading...\n")

# Displaying splash to console and logfile
# Splash end

#!SECTION Checking if config file exists
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as config:
        configData = json.load(config)
        ffmpeg_path = configData["FFMPEG_PATH"]
        ytdl_path = configData["YTDL_PATH"]

        if ffmpeg_path == "" or ytdl_path == "":
            print("Fields in config.json are invalid, please check again, and restart the bot")
            exit()

else:
    print("config.json does not exist in the current directory!")
    configTemplate = {"FFMPEG_PATH": "", "YTDL_PATH": ""}

    with open(CONFIG_PATH, "w+") as f:
        json.dump(configTemplate, f)
        print("created config template")
        print("\nPlease fill in the ffmpeg and yt-dlp path in the config.json file to continue")
        exit()


#!SECTION Checking if TOKEN file exists
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH) as tokens:
        tokenData = json.load(tokens)
        dev_token = tokenData["DEV_TOKEN"]
        prod_token = tokenData["PROD_TOKEN"]
    
    if dev_token == "" or prod_token == "":
            print("Fields in token.json are invalid, please check again, and restart the bot")
            exit()
else:
    print("File token.json does not exist")
    configTemplate = {"PROD_TOKEN": "", "DEV_TOKEN": ""}

    with open(TOKEN_PATH, "w+") as f:
        json.dump(configTemplate, f)
        print("Created token config template")
        print("\nPlease fill in the tokens in your token.json and restart the bot!")
        exit()

async def badWords():
    #!SECTION Checking if TOKEN file exists
    if os.path.exists(BADWORDS_PATH):
        with open(BADWORDS_PATH) as badwords:
            badWordsData = json.load(badwords)
            global badWordsDict
            badWordsDict = badWordsData["badwords"]
        
        if not badWordsDict:
                print("There are no banned words specified.\n Fill in the badwords.json and restart the bot")
                exit()
    else:
        print("File badwords.json does not exist")
        configTemplate = {"badwords": ["word1", "word2"]}

        with open(BADWORDS_PATH, "w+") as f:
            json.dump(configTemplate, f)
            print("Created bad words file template")
            print("\nPlease fill in the bad words list to continue!")
            exit()

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

async def update_ytdlp():
    if(is_os_windows):
        command = f"{ytdl_path} -U"

    else:
        command = f"{ytdl_path} -U"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    while (process.poll() != 0):
        time.sleep(1)
        await logger(1, "Waiting for yt-dlp to update...")

async def dbInit():
    await logger(1, "Setting up database connection")
    try:
        global database
        if(is_os_windows == True):
            database = sqlite3.connect("bot.db")
        else:
            database = sqlite3.connect("bot.db")

        # Read database initialisation
        if(is_os_windows == True):
            loadDB = open('.\\assets\\initialDB.sql')
        else:
            loadDB = open('./assets/initialDB.sql')

        dbstring = loadDB.read().split("--A")

        cursor = database.cursor()

        for command in dbstring:
            cursor.execute(command)
            database.commit()

        cursor.close()
        loadDB.close()
        await logger(1, "Database initialisation complete")

    except sqlite3.Error as e:
        await logger(3, f"Error initialising database\n{e}")
        exit()

async def dbconn():
    try:
        if(is_os_windows == True):
            database = sqlite3.connect(".\\bot.db")
        else:
            database = sqlite3.connect("./bot.db")
        
        return database
    except Exception as e:
        await logger(3, "An error occured while attempting database r/w")

bot = commands.Bot(command_prefix="", intents= discord.Intents.all())

@bot.event
async def on_ready():
    await logger(1, "Loading list of banned words")
    await badWords()

    global is_os_windows
    if(platform.system() == "Windows"):
        is_os_windows = True
        await logger(2, "Bot running on Windows, using \"\\\" as path separator")
    else:
        is_os_windows = False
        await logger(2, "Bot not running on Windows, using \"/\" as path separator")
    
    if(IS_BOT_DEV):
        await logger(2, "Bot was launched as a test instance")
    else:
        await logger(2, "Bot was launched as a live instance")

    await logger(1, "Sanitising audio folder...")
    await audio_delete()

    await logger(1, "Updating yt-dlp...")
    await update_ytdlp()

    await logger(1, "Initialising database...")
    await dbInit()


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
    await interaction.response.send_message(f"*Pong!*\n`Current latency is {latency} ms`", ephemeral=True)
    await logger(1, f"Current ping is {latency}ms")

@bot.tree.command(name="echo")
@app_commands.describe(echo_content = "Content after the \"/echo\" command that gets echoed back")
async def echo(interaction: discord.Interaction, echo_content: str):
    """Echo the content"""
    await interaction.response.send_message(f"`{echo_content}`")

@bot.tree.command(name="about")
async def about(interaction: discord.Interaction):
    """Information about the bot"""
    response: str = f"*Hyperion {BOT_VERSION}*\nCreated by: github.com/balika0105\nUse `/commands` for more info!"
    await logger(4, f"\"about\" command was called by {interaction.user.name}#{interaction.user.discriminator}")
    await interaction.response.send_message(f"{response}")


@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):
    """Join voice channel"""
    if interaction.user.voice is not None:
        voicechannel = interaction.user.voice.channel
        msgchannel = interaction.channel
        await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} called the bot into \"{voicechannel.name}\" voice channel")
        await interaction.response.send_message(f"I am now attempting to join this voice channel: {voicechannel.mention}", ephemeral=True)
        try:
            global voiceclient
            voiceclient = await voicechannel.connect(self_deaf=True)
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
            await interaction.response.send_message(f"Starting voice test in voice channel: `{voicechannel.mention}`")
            try:
                global voiceclient
                voiceclient = await voicechannel.connect(self_deaf=True)
                
            except Exception as ex:
                await msgchannel.send("An error occured!")
                await logger(3, f"An exception occured: {ex}")

            if is_os_windows:
                sourcefile = FFmpegPCMAudio(".\\assets\\bot_test_voice.mp3", executable=ffmpeg_path)
            else:
                sourcefile = FFmpegPCMAudio("./assets/bot_test_voice.mp3", executable=ffmpeg_path)
            player = voiceclient.play(sourcefile)
        else:
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} tried to invite bot to voice, but user isn't in a voice channel!")
            await interaction.response.send_message("You are not connected to a voice channel!", ephemeral=True)
    except Exception as ex:
        await interaction.response.send_message(f"An error occured! Most likely you're not in a voice channel!", ephemeral=True)
        await logger(3, f"An exception occured while running the bot\n\t{ex}")


def download_music(url: str):
    # Generating a random string for destination
    letters = string.ascii_lowercase
    outputstring = ''.join(random.choice(letters) for i in range(10))

    if(is_os_windows):
        command = [f"{ytdl_path}", f"{url}", "-f", "251", "-x", "--audio-format", "mp3", "--output", f".\\au_temp\\{outputstring}"]
        #command = f"{ytdl_path} {url} -f 251 -x --audio-format mp3 --output \".\\au_temp\\{outputstring}\""

    else:
        command = [f"{ytdl_path}", f"{url}", "-f", "251", "-x", "--audio-format", "mp3", "--output", f"./au_temp/{outputstring}"]
        #command = f"{ytdl_path} {url} -f 251 -x --audio-format mp3 --output \"./au_temp/{outputstring}\""      
    result = subprocess.run(command)

    return outputstring


playQueueUrls = []
playQueueFiles = []

async def queueHandler():
    await logger(1, "Called queueHandler")
    while (len(playQueueUrls) > 0):
        # "Pop" the first item of the URL list, so we can store it and
        # it gets removed from the list/array/whatever
        url = playQueueUrls.pop(0)
        result = download_music(url)
        outputstring = result
        sourcepath: str = ""

        if(is_os_windows):
            sourcepath = f".\\au_temp\\{outputstring}.mp3"
        else:
            sourcepath = f"./au_temp/{outputstring}.mp3"

        playQueueFiles.append(sourcepath)

def queueHandlerCall():
    # We need to do it this way otherwise, it ain't async
    asyncio.run(queueHandler())


@bot.tree.command(name="play")
@app_commands.describe(url = "YouTube video URL")
async def play(interaction: discord.Interaction, url: str):
    """Music playback from YouTube (only available with URL, no search)"""
    msgchannel = interaction.channel
    try:
        if interaction.user.voice is not None:
            voicechannel = interaction.user.voice.channel
            
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} called the bot into \"{voicechannel.name}\" voice channel to play media")
            try:
                global voiceclient
                if not voiceclient.is_connected():
                    voiceclient = await voicechannel.connect(self_deaf=True)
                    if(is_os_windows):
                        pingsourcefile = FFmpegPCMAudio(f".\\assets\\wait.mp3", executable=ffmpeg_path)
                    else:
                        pingsourcefile = FFmpegPCMAudio(f"./assets/wait.mp3", executable=ffmpeg_path)

                    voiceclient.play(pingsourcefile)
                    while voiceclient.is_playing():
                        await asyncio.sleep(1)

                
            except Exception as ex:
                await logger(3, f"An exception occured: {ex}")

            if not voiceclient.is_playing():
                try:
                    await interaction.response.send_message(f"Starting playback of {url} for {voicechannel.mention}", ephemeral=True)
                    await logger(1, "Start audio download")
                    result = await bot.loop.run_in_executor(None, download_music, url)
                    await logger(1, "Stop audio download")
                    outputstring = result
                    await logger(1, f"Output string: {outputstring}")

                    
                    voiceclient.stop()
                    sourcepath: str = ""
                    if(is_os_windows):
                        sourcepath = f".\\au_temp\\{outputstring}.mp3"
                    else:
                        sourcepath = f"./au_temp/{outputstring}.mp3"

                    sourcefile = FFmpegPCMAudio(sourcepath, executable=ffmpeg_path)
                    await logger(1, f"Starting playback in voice channel {voiceclient.channel.name}")
                    player = voiceclient.play(sourcefile)

                    while voiceclient.is_playing():
                        await asyncio.sleep(1)

                    # Auto-sanitising the music downloads folder
                    os.remove(sourcepath)

                    # Playing the queue if exists
                    while (len(playQueueFiles) > 0):
                        sourcepath = playQueueFiles.pop(0)
                        sourcefile = FFmpegPCMAudio(sourcepath, executable=ffmpeg_path)
                        await logger(1, f"Starting playback from queue in voice channel {voiceclient.channel.name}")
                        player = voiceclient.play(sourcefile)

                        while voiceclient.is_playing():
                            await asyncio.sleep(1)

                        os.remove(sourcepath)

                    voiceclient.stop()


                except Exception as ex:
                    await msgchannel.send("An error occured!")
                    await logger(3, f"An exception occured: {ex}")

            elif voiceclient.is_playing():
                # Adding link to queued URLs
                await interaction.response.send_message(f"Added {url} to queue", ephemeral=True)
                playQueueUrls.append(url)

                queueThread = threading.Thread(target=queueHandlerCall)
                if not queueThread.is_alive():
                    queueThread.start()

        else:
            await logger(1, f"{interaction.user.name}#{interaction.user.discriminator} tried to invite bot to voice, but user isn't in a voice channel!")
            await interaction.response.send_message("You are not connected to a voice channel!", ephemeral=True)
    except Exception as ex:
        await interaction.response.send_message("An error occured while processing your request!", ephemeral=True)
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
    response: str = ""
    cmdfetch = await bot.tree.fetch_commands()
    for cmd in cmdfetch:
        if not "ADMIN ONLY" in cmd.description:
            response = response + "`/" + cmd.name + "`: " + cmd.description + "\n"

    await interaction.response.send_message(f"Available commands: \n{response}", ephemeral=True)


@bot.tree.command(name="stats")
async def stats(interaction: discord.Interaction):
    """Get your messaging stats"""
    try:
        database = await dbconn()
        c = database.cursor()
        query = c.execute(f"SELECT xp, userlevel FROM levels WHERE uid = {interaction.user.id}")
        result = query.fetchone()

        if result is None:
            #Couldn't find user
            await interaction.response.send_message(f"*I couldn't find you in the database*", ephemeral=True)
        else:
            # We found the user
            xp, level = result
            await interaction.response.send_message(f"*{interaction.user.name}#{interaction.user.discriminator}'s stats*\nXP: `{xp}xp`\nLevel: `{level}`", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"*An error occured trying to fetch your stats*", ephemeral=True)
        await logger(3, f"An error occured when trying to access user stats:\n{e}")


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
    """ADMIN ONLY: Send a test DM to the selected user"""
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
        await interaction.response.send_message(f"You don't have the rights to perform this action", ephemeral=True)
    

@bot.tree.command(name="sanitiselog")
async def sanitiselog(interaction: discord.Interaction):
    """ADMIN ONLY: Sanitise log files"""
    await logger(1, f"User {interaction.user.name}#{interaction.user.discriminator} wants sanitise log files through the bot")
    sender = interaction.user
    if(await isUserAdmin(sender)):
        # Proceed
        print("Flushing log file...")
        try:
            open('bot.log', 'w').close()
            await logger(1, f"Log file has been sanitised by user {interaction.user.name}#{interaction.user.discriminator}, started new log file")
            await interaction.response.send_message(f"Log file flush OK, started new log file", ephemeral=True)
        except Exception as e:
            print(f"FAILED TO REMOVE LOG FILE\n{e}")
    else:
        await interaction.response.send_message(f"You don't have the rights to perform this action!", ephemeral=True)

#######################################


######### MESSAGE MODERATION #########
@bot.event
async def on_message(message):
#await logger(1, f"Message sent!\nServer: {message.guild.name}\nChannel: {message.channel.name}\nAuthor: {message.author.name}#{message.author.discriminator}\nMessage: {message.content}")
    if message.author == bot.user:
        return
    else:
        # Returns true if it contains a banned word
        if await messageCheck(message.content):
            await logger(4, f"{message.author.name}#{message.author.discriminator} (UID: {message.author.id} sent an offensive message:\n{message.content}")
            await message.channel.send(f"{message.author.mention} ! Do not use banned words!")
            await message.delete()
        else:
            # Increase user XP
            # They shouldn't get XP for swearwords lol
            try:
                database = await dbconn()
                c = database.cursor()
                result = c.execute(f"SELECT xp, userlevel FROM levels WHERE uid = \"{message.author.id}\"")
                

                msgwords = message.content.split(' ')
                msglen = len(msgwords)

                row = result.fetchone()

                if row is None:
                    # User isn't in database, new chatter
                    xp = msglen
                    level = msglen // 100

                    c.execute(f"INSERT INTO levels (xp, userlevel, uid) VALUES ({xp}, {level}, {message.author.id})")
                    database.commit()
                    c.close()
                    database.close()
                    await message.channel.send(f"{message.author.mention} just started chatting!")

                else:
                    # User is already in database, increase XP
                    xp, level = row

                    newxp = xp + msglen
                    newlevel = newxp // 100

                    # Updating values
                    c.execute(f"UPDATE levels SET xp = {newxp}, userlevel = {newlevel} WHERE uid = {message.author.id}")
                    database.commit()
                    c.close()
                    database.close()

                    if(newlevel > level):
                        await message.channel.send(f"{message.author.mention} has levelled up and is now Level {newlevel}!")

            except Exception as e:
                #
                await logger(3, f"An error occured while trying to manipulate the database\n{e}")

        

async def messageCheck(message):
    pattern = r"\b(" + "|".join(map(re.escape, badWordsDict)) + r")\b"
    matches = re.findall(pattern, message, re.IGNORECASE)
    if matches:
        return True
    else:
        return False


if(IS_BOT_DEV):
    # Log in as test instance
    bot.run(dev_token)
else:
    # Log in as live instance
    bot.run(prod_token)
