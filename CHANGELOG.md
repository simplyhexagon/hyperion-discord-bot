# Hyperion Discord Bot - Changelog

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