# Hyperion Discord Bot
Main repo for the Hyperion Discord Bot (Engine/Base)

This bot is made in python3, to launch, use `python3 ./bot.py`

Required modules to launch the bot
- `discord`
- `pynacl`

Install these modules using the following commands
- Windows or Arch Linux `python3 -m pip install #module name`
- Debian `apt install python3-discord python3-nacl`

If you don't have pip installed on your system yet, please search the internet how to install pip on your platform  
If your system tells you that installing python modules with pip might break system packages, it is recommended to install those modules with your system's package manager (*Debian* example)

### How to use?

On first launch the bot generates a few configuration files in `/configs` which have to be filled in
- `config.json`
    - Path to `ffmpeg` executable
    - Path to `yt-dlp` executable
    - Role IDs of higher ranked roles on your server
- `badwords.json`
    - List of banned words on your server
- `token.json`
    - Production token
        - Token used for deploying the discord bot in "production"
    - Development token
        - Token used if you have a separate application registered as your "test build"

### ffmpeg and yt-dlp

If you want to use the code as-is, you will need to install `ffmpeg` and `yt-dlp` on your system.  
Since those are open source software, we cannot bundle those

### Level system

Each user on the server levels up after 100 words sent every time.
Chat level is calculated based on the number of words they sent in each of their messages, divided by 100

- `xp` = word count (space separated characters, yes, even the mighty *xnopyt*)
- `level` = `xp` / 100, rounded to the nearest integer

### configs/config.json

FFMPEG_PATH: string - Path to ffmpeg executable (e.g. `C:\ffmpeg\bin\ffmpeg.exe` or `/usr/bin/ffmpeg`)

YTDL_PATH: string - Path to yt-dlp executable (e.g. `C:\yt-dlp\bin\yt-dlp.exe` or `/usr/bin/yt-dlp`)

ADMIN_ROLES: array[int] - List of roles that are admin on the server (USE NUMBERS)

### hyperion-bot.service.template

This is a template file for a `systemd` service to automatically start the bot after a reboot.

Edit the contents of the file to fit your use case, then copy it to `/etc/systemd/system`
then run `# systemctl enable --now hyperion-bot`

To see the logs, use `# systemctl status hyperion-bot`

### assets/initialDB.sql

This is the bot's SQL script to build its database from

Please note that the instructions are split with `--A`, since otherwise the SQLite engine would try to execute
them simultaneously, which is not allowed.

If you'd like to expand the database to your own liking, always split the instructions with `--A`