# Telegram Bot Setup Guide

This guide will help you set up and run AppleMusicDecrypt as a Telegram bot.

## Prerequisites

1. Python 3.11 or higher
2. Poetry (for dependency management)
3. A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

## Setup Steps

### 1. Install Dependencies

```bash
# Install system dependencies (if needed)
bash ./tools/install-deps.sh

# Install Python dependencies
poetry install
```

### 2. Configure the Bot

```bash
# Copy the example configuration
cp config.example.toml config.toml

# Edit config.toml and add your Telegram bot token
nano config.toml
```

In `config.toml`, update the `[telegram]` section:

```toml
[telegram]
# Get this token from @BotFather on Telegram
bot_token = "YOUR_BOT_TOKEN_HERE"

# Optional: List of admin user IDs
admin_users = []

# Maximum file size for uploads (in MB, Telegram limit is 2000MB)
max_file_size = 2000

# Temporary download directory
temp_dir = "telegram_downloads"
```

### 3. Configure Wrapper-Manager

Make sure you have a wrapper-manager instance configured in the `[instance]` section:

```toml
[instance]
url = "wm.wol.moe"  # Or your own wrapper-manager instance
secure = true
```

For testing, you can use the public instance:
```toml
[instance]
url = "wm.wol.moe"
secure = true
```

### 4. Run the Bot

```bash
# Run as Telegram bot
poetry run python main.py --telegram

# Or run as CLI (original mode)
poetry run python main.py
```

## Using the Bot

### Commands

- `/start` - Show welcome message and help
- `/help` - Show help message
- `/login` - Login with your Apple Music account
- `/logout` - Logout from your account
- `/status` - Check wrapper-manager status

### Login Flow

1. Send `/login` to the bot
2. Bot will ask for your Apple ID (email)
3. Send your Apple ID
4. Bot will ask for your password
5. Send your password (it will be deleted immediately)
6. If 2FA is enabled, bot will ask for the 2FA code
7. Send your 2FA code
8. You're logged in!

### Downloading Music

Once logged in, simply send any Apple Music URL to the bot:

**Supported URLs:**
- Song: `https://music.apple.com/jp/song/caribbean-blue/339592231`
- Album: `https://music.apple.com/jp/album/nameless-name-single/1688539265`
- Playlist: `https://music.apple.com/jp/playlist/bocchi-the-rock/pl.u-Ympg5s39LRqp`
- Artist: `https://music.apple.com/jp/artist/エンヤ/160847`

The bot will:
1. Download the music
2. Decrypt it
3. Send the file(s) back to you via Telegram

### Supported Codecs

The bot uses ALAC (lossless) codec by default. Other supported codecs:
- `alac` - Apple Lossless (default)
- `ec3` - Dolby Digital Plus (Atmos)
- `ac3` - Dolby Digital
- `aac` - AAC stereo
- `aac-binaural` - AAC binaural
- `aac-downmix` - AAC downmix

## Limitations

1. **File Size**: Telegram bots can send files up to 2GB (2000MB)
2. **Rate Limits**: Telegram has rate limits on bot messages and file uploads
3. **Concurrent Downloads**: Controlled by `parallelNum` in config.toml
4. **Single Songs Only**: Currently, the bot only sends individual song files. For albums/playlists, files are saved to the downloads directory.

## Troubleshooting

### Bot doesn't respond
- Check if the bot token is correct
- Make sure the bot is running (`poetry run python main.py --telegram`)
- Check the logs for errors

### Login fails
- Verify your Apple ID and password are correct
- Make sure 2FA code is entered within 5 minutes
- Check if wrapper-manager is accessible (`/status` command)

### Download fails
- Check if you're logged in (`/status` command)
- Verify the Apple Music URL is valid
- Check wrapper-manager status
- Look at the logs for detailed error messages

### File not sent
- Check if file size exceeds Telegram's 2GB limit
- Verify the download completed successfully
- Check the `telegram_downloads` directory for the file

## Security Notes

1. **Password Security**: Your password is deleted immediately after being processed
2. **Session Storage**: User sessions are stored locally in `user_sessions.json`
3. **Private Bot**: Keep your bot token private and don't share it
4. **Admin Users**: You can restrict certain features to admin users by adding their Telegram user IDs to `admin_users` in config.toml

## Advanced Configuration

### Custom Download Paths

You can customize where files are saved by editing the `[download]` section in `config.toml`:

```toml
[download]
dirPathFormat = "downloads/{album_artist}/{album}"
playlistDirPathFormat = "downloads/playlists/{playlistName}"
songNameFormat = "{disk}-{tracknum:02d} {title}"
```

### Codec Selection

To change the default codec, modify the `codecPriority` in config.toml:

```toml
[download]
codecPriority = ["alac", "ec3", "ac3", "aac"]
```

### Parallel Downloads

Adjust concurrent downloads:

```toml
[download]
parallelNum = 3  # Number of concurrent downloads
maxRunningTasks = 128  # Maximum running tasks
```

## Running as a Service

### Using systemd (Linux)

Create a service file `/etc/systemd/system/apple-music-bot.service`:

```ini
[Unit]
Description=Apple Music Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AppleMusicDecrypt
ExecStart=/usr/bin/poetry run python main.py --telegram
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable apple-music-bot
sudo systemctl start apple-music-bot
sudo systemctl status apple-music-bot
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy project files
COPY . .

# Install Python dependencies
RUN poetry install --no-dev

# Run the bot
CMD ["poetry", "run", "python", "main.py", "--telegram"]
```

Build and run:
```bash
docker build -t apple-music-bot .
docker run -d --name apple-music-bot \
  -v $(pwd)/config.toml:/app/config.toml \
  -v $(pwd)/downloads:/app/downloads \
  apple-music-bot
```

## Support

For issues and questions:
- GitHub Issues: [AppleMusicDecrypt Issues](https://github.com/WorldObservationLog/AppleMusicDecrypt/issues)
- Telegram Group: https://t.me/apple_music_alac
