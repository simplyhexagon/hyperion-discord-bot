# Hyperion Discord Bot (Engine?)
Main repo for the Hyperion Discord Bot (Engine/Base)

This bot is made in python3, to launch, use `python3 ./bot.py`

Required modules to launch the bot
- `discord`
- `pynacl`

Install these modules using `python3 -m pip install #module name`

If you don't have pip installed on your system yet, please search the internet how to install pip on your platform

### How to use?

On first launch the bot generates a `config.json` which it will read on the next launch.

Before the 2nd startup, please fill in the contents appropriately
- Path to ffmpeg
- Path to yt-dlp
- Production token
    - Token used for deploying the discord bot in "production"
- Development token
    - Token used if you have a separate application registered as your "test build"

### ffmpeg and yt-dlp

If you want to use the bot as-is, you will need to add `yt-dlp` and `ffmpeg` to the appropriate folders

Since these are open-source softwares, we cannot include them in this package

### configs/badwords.json

This configuration file will be automatically created, but you will have to fill it out for yourself

### Level system

Each chatter on the server levels up after 100 words sent every time.
Chat level is calculated based on the number of words they sent in each of their messages, divided by 100

xp = word count (space separated characters, yes, even xnopyt)
level = xp / 100, rounded to the nearest integer