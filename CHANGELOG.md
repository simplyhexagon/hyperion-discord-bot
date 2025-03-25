# Hyperion Discord Bot - Changelog

2025-03-26
- Removed code that still used the "discriminators" from Discord, as they have moved onto the `@username` system.
- The `configs` folder is now properly part of the repo with an appropriate `.gitignore`
- Temporarily moved the old version to `bot.py.old`
- Change the splash to a one-liner. More difficult to read, easier to interpret for Python

- Bumped vernum to 0.8

2023-06-27
- Removed remainders of pytube implementation
- The bot now downloads audios named as the YouTube video ID, instead of a randomly generated name
- Caching added for media files, so they don't get downloaded again if unnecessary
- Implemented auto-leave when idle

2023-06-24
- Wanted to implement pytube, but it is apparently broken, so it wasn't used
- Attempt to implement an automatic leave if bot is idle for 2 minutes

2023-06-21
- Updated `README.md` to include more info
- Added `systemd` service template
- Handle error that occurs if `yt-dlp` is installed with `apt` or similar, and we cannot force the update with `yt-dlp -U`
- Added a few embeds to make the reply *more pretty*

2023-06-20
- Update README
- Removed `ffmpeg` and `yt-dlp` directories, as the bot uses those software differently now

2023-06-19
- Minor code fixes
- Version number increment
- Admin roles are moved to config.json, see README

2023-06-18:
- Minor code fixups
- Playback queue implementation
    - Skip command
- Dynamic list of available commands
- Update version number

2023-06-04:
- Introduced CHANGELOG
- Introduced database system
- Splash screen added
- Minor tweaks with logging
- User chat level system added