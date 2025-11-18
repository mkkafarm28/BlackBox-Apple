# Quick Start Guide - Telegram Bot

## 🚀 5-Minute Setup

### 1. Get Bot Token
1. Open Telegram → Search `@BotFather`
2. Send: `/newbot`
3. Follow instructions
4. Copy your token: `123456789:ABC...`

### 2. Configure
```bash
cp config.example.toml config.toml
nano config.toml  # or use any text editor
```

Edit these lines:
```toml
[telegram]
botToken = "PASTE_YOUR_TOKEN_HERE"
enable = true
```

### 3. Install & Run
```bash
poetry install
poetry run python telegram_main.py
```

### 4. Use Your Bot
1. Find your bot in Telegram
2. Send: `/start`
3. Send any Apple Music URL
4. Receive your music! 🎵

---

## 📱 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show welcome & help | `/start` |
| `/download <url>` | Download music | `/download https://music.apple.com/...` |
| `/dl <url>` | Short download | `/dl https://music.apple.com/...` |
| `/status` | Check system status | `/status` |
| `/help` | Show help | `/help` |

## 🎵 Supported Content

✅ Songs  
✅ Albums  
✅ Artists (all albums)  
✅ Playlists  

## 🎛️ Codec Options

Add codec after URL:
```
/download <url> alac    ← Lossless (default)
/download <url> aac     ← Compressed
/download <url> ec3     ← Atmos
```

Available: `alac`, `ec3`, `ac3`, `aac`, `aac-binaural`, `aac-downmix`, `aac-legacy`

## 💡 Pro Tips

1. **Just paste URLs** - No need for `/download` command
2. **File size limit** - Default 50MB (configurable)
3. **Multiple users** - Bot handles many users simultaneously
4. **Metadata included** - Cover art, lyrics, tags all embedded

## ⚠️ Troubleshooting

**Bot not responding?**
- Check token in config.toml
- Verify `enable = true`
- Check console for errors

**Can't connect?**
- Check internet connection
- Try public instance: `url = "wm.wol.moe"`

**File too large?**
- Increase `maxFileSize` in config
- Or use lower quality codec (aac)

## 📚 Full Documentation

- English: [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md)
- မြန်မာ: [TELEGRAM_BOT_SETUP_MM.md](TELEGRAM_BOT_SETUP_MM.md)
- Changes: [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)

## 🆘 Need Help?

- GitHub: https://github.com/WorldObservationLog/AppleMusicDecrypt
- Telegram: https://t.me/apple_music_alac

---

**That's it! Enjoy your music! 🎶**
