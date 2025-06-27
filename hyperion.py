#!/usr/bin/env python3

# Hyperion Discord Bot by @simplyhexagon
# Rewrite attempt

# Imports

# Discord stuff
import discord

# Discord slash commands
from discord import app_commands
from discord.ext import commands

# Discord playback to voicechat
from discord import FFmpegPCMAudio

# Asynchronous operations
import asyncio

import logging # Proper logging
import datetime # For writing datetime to log
import nacl # Discord voicechat dependency

import json # Configuration file I/O
import os # Creating and removing files, checking if they exist
import platform # Checking if the bot is running on windows
import time
import string # String formatting
import subprocess # Used in /play for first download
import threading # So far it's only used for queue download


from urllib.parse import urlparse, parse_qs # Parse youtube URL

import sqlite3 # Database

# For moderation
import re

# Constants
IS_BOT_DEV = True
BOT_VERSION: str = "test_2.0"

CONFIG_PATH: str = "./configs/config.json"
TOKEN_PATH: str = "./configs/token.json"
BADWORDS_PATH: str = "./configs/badwords.json"
admin_roles = []

# Vars
global is_os_windows
is_os_windows = False
global database

global badWordsDict
badWordsDict = []

global playQueueUrls
global playQueueFiles

# Format: [URL/filename , Room ID]
playQueueUrls = [[]]
playQueueFiles = [[]]

# Setting up log file
log = logging.basicConfig(filename='hyperion.log', encoding='utf-8', format='%(asctime)s | [%(levelname)s] %(message)s', level=logging.DEBUG, datefmt = "%Y-%m-%d %H:%M:%S")

# Start msg
startmsg = f"Starting Hyperion Discord Bot, version {BOT_VERSION}..."
logging.warning(startmsg)
print(startmsg)


# Logger function
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
# Logger function END


#@bot.event
#async def on_ready():
