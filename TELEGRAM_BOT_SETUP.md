# Telegram Bot Setup Guide

This guide will help you set up the Apple Music Download Telegram Bot.

## Prerequisites

1. Python 3.11 or higher
2. Poetry (Python package manager)
3. A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Configure the Bot

1. Copy the example configuration:
   ```bash
   cp config.example.toml config.toml
   ```

2. Edit `config.toml` and update the Telegram section:
   ```toml
   [telegram]
   botToken = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual bot token
   enable = true                      # Enable Telegram bot mode
   maxFileSize = 50                   # Maximum file size in MB to upload
   ```

3. Configure the wrapper-manager instance:
   ```toml
   [instance]
   url = "wm.wol.moe"  # Or your own wrapper-manager instance
   secure = true
   ```

## Step 3: Install Dependencies

```bash
# Install system dependencies (if needed)
bash ./tools/install-deps.sh

# Install Python dependencies
poetry install
```

## Step 4: Run the Bot

```bash
poetry run python telegram_main.py
```

You should see:
```
✅ Telegram Bot initialized successfully!
🤖 Starting Telegram Bot...
Bot is ready to receive messages!
```

## Step 5: Use the Bot

1. Open Telegram and search for your bot by username
2. Send `/start` to begin
3. Send an Apple Music URL or use `/download <url>`

### Available Commands

- `/start` - Show welcome message and help
- `/help` - Show available commands
- `/download <url>` - Download song/album/playlist from Apple Music
- `/dl <url>` - Short version of download command
- `/status` - Check wrapper-manager status

### Supported URLs

- Apple Music Song: `https://music.apple.com/jp/song/caribbean-blue/339592231`
- Apple Music Album: `https://music.apple.com/jp/album/nameless-name-single/1688539265`
- Apple Music Artist: `https://music.apple.com/jp/artist/...`
- Apple Music Playlist: `https://music.apple.com/jp/playlist/...`

### Download Options

You can specify codec after the URL:
```
/download https://music.apple.com/... alac
/download https://music.apple.com/... aac
/download https://music.apple.com/... ec3
```

Available codecs: `alac`, `ec3`, `ac3`, `aac`, `aac-binaural`, `aac-downmix`, `aac-legacy`

## Features

✅ Download songs, albums, artists, and playlists  
✅ Multiple codec support (ALAC, AAC, EC3, AC3)  
✅ Automatic file upload to Telegram  
✅ Progress notifications  
✅ Metadata embedding (title, artist, album, cover art)  
✅ Lyrics support (.lrc files)  
✅ Multi-user support  

## Troubleshooting

### Bot doesn't respond
- Check if the bot token is correct in `config.toml`
- Make sure `telegram.enable = true`
- Check the console for error messages

### "Unable to connect to wrapper-manager"
- Check your internet connection
- Verify the wrapper-manager URL in config
- Try using the public instance: `wm.wol.moe`

### Files are too large to upload
- Increase `maxFileSize` in config (Telegram limit is 50MB for bots)
- Files larger than the limit will be saved locally only

### Download fails
- Check if the Apple Music URL is valid
- Verify wrapper-manager has available accounts (`/status` command)
- Check console logs for detailed error messages

## Running as a Service (Linux)

Create a systemd service file `/etc/systemd/system/apple-music-bot.service`:

```ini
[Unit]
Description=Apple Music Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AppleMusicDecrypt
ExecStart=/usr/bin/poetry run python telegram_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable apple-music-bot
sudo systemctl start apple-music-bot
sudo systemctl status apple-music-bot
```

## Security Notes

- Keep your bot token secret
- Don't share your `config.toml` file
- Consider restricting bot access to specific users if needed
- Files are saved locally in the `downloads/` directory

## Support

For issues and questions:
- GitHub Issues: https://github.com/WorldObservationLog/AppleMusicDecrypt/issues
- Telegram Group: https://t.me/apple_music_alac

## License

Same as AppleMusicDecrypt project license.
