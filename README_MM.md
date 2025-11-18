# AppleMusicDecrypt - Telegram Bot

Apple Music သီချင်းများကို ဒေါင်းလုဒ်လုပ်ပေးသော Telegram Bot

## 🎉 အသစ်ထွက်ရှိသော လုပ်ဆောင်ချက်

ဤ tool သည် ယခု **Telegram Bot** အဖြစ် အလုပ်လုပ်နိုင်ပါပြီ! သင့် bot သို့ Apple Music link များ ပို့ပြီး သီချင်းများကို တိုက်ရိုက် ရယူနိုင်ပါသည်။

## 🚀 အမြန်စတင်ရန်

### ၁. Bot Token ရယူပါ
```
Telegram → @BotFather → /newbot
```

### ၂. Configuration ပြင်ဆင်ပါ
```bash
cp config.example.toml config.toml
nano config.toml
```

```toml
[telegram]
botToken = "သင့် TOKEN ထည့်ပါ"
enable = true
```

### ၃. စတင်ပါ
```bash
poetry install
poetry run python telegram_main.py
```

### ၄. အသုံးပြုပါ
```
Telegram တွင် သင့် bot ကို ရှာပါ
/start ပို့ပါ
Apple Music URL ပို့ပါ
သီချင်း ရယူပါ! 🎵
```

## 📱 Commands များ

| Command | ရှင်းလင်းချက် |
|---------|---------------|
| `/start` | စတင်ရန် |
| `/download <url>` | ဒေါင်းလုဒ်လုပ်ရန် |
| `/dl <url>` | အတိုကောက် |
| `/status` | အခြေအနေစစ်ရန် |
| `/help` | အကူအညီ |

## 🎵 ပံ့ပိုးမှုများ

✅ သီချင်းများ (Songs)  
✅ အယ်လ်ဘမ်များ (Albums)  
✅ အနုပညာရှင်များ (Artists)  
✅ Playlists များ  

## 🎛️ အရည်အသွေး ရွေးချယ်မှု

```
/download <url> alac    ← အကောင်းဆုံး (Lossless)
/download <url> aac     ← ပုံမှန် (Compressed)
/download <url> ec3     ← Atmos
```

## 💡 အသုံးဝင်သော အကြံပြုချက်များ

1. **URL တိုက်ရိုက်ပို့ပါ** - `/download` မလိုပါ
2. **File size limit** - Default 50MB
3. **အသုံးပြုသူ အများအပြား** - တစ်ချိန်တည်းတွင် အသုံးပြုနိုင်
4. **Metadata ပါဝင်** - Cover art, lyrics, tags အားလုံး

## 📚 အသေးစိတ် လမ်းညွှန်များ

- **အမြန်စတင်ရန်**: [QUICK_START.md](QUICK_START.md)
- **အပြည့်အစုံ Setup**: [TELEGRAM_BOT_SETUP_MM.md](TELEGRAM_BOT_SETUP_MM.md)
- **English Guide**: [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md)
- **Technical Details**: [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- **Workflow Diagram**: [BOT_WORKFLOW.md](BOT_WORKFLOW.md)

## ⚙️ လုပ်ဆောင်ချက်များ

### ✅ အဓိက လုပ်ဆောင်ချက်များ
- Telegram bot integration
- Command-based interface
- တိုက်ရိုက် URL ပို့ခြင်း
- အသုံးပြုသူ အများအပြား ပံ့ပိုးမှု

### ✅ Download လုပ်ဆောင်ချက်များ
- Apple Music content အားလုံး ပံ့ပိုးမှု
- Codec အမျိုးမျိုး (ALAC, AAC, EC3, AC3)
- အလိုအလျောက် Telegram သို့ upload
- File size စစ်ဆေးမှု

### ✅ အသုံးပြုသူ အတွေ့အကြုံ
- Progress အကြောင်းကြားချက်များ
- Error handling
- Wrapper-manager status စစ်ဆေးမှု
- Metadata ပြည့်စုံသော audio files

## 🔧 ပြဿနာ ဖြေရှင်းခြင်း

### Bot က တုံ့ပြန်မှု မရှိပါက
```bash
# Token စစ်ဆေးပါ
cat config.toml | grep botToken

# Enable စစ်ဆေးပါ
cat config.toml | grep "enable = true"

# Logs ကြည့်ပါ
poetry run python telegram_main.py
```

### Connection ပြဿနာ
```toml
[instance]
url = "wm.wol.moe"  # Public instance သုံးပါ
secure = true
```

### File အရွယ်အစား ကြီးလွန်းပါက
```toml
[telegram]
maxFileSize = 50  # တိုးမြှင့်ပါ (သို့) codec ပြောင်းပါ
```

## 🏗️ System Architecture

```
User (Telegram)
    ↓
telegram_main.py
    ↓
telegram_bot.py (Bot Manager)
    ↓
telegram_handlers.py (Commands)
    ↓
rip.py (Download Engine)
    ↓
telegram_integration.py (File Sender)
    ↓
User (Receives File)
```

## 📁 ဖိုင်များ တည်နေရာ

```
AppleMusicDecrypt/
├── telegram_main.py          # Bot entry point
├── config.toml               # Configuration
├── QUICK_START.md            # အမြန်စတင်ရန်
├── TELEGRAM_BOT_SETUP_MM.md  # မြန်မာ လမ်းညွှန်
├── BOT_WORKFLOW.md           # Technical diagram
└── src/
    ├── telegram_bot.py       # Bot manager
    ├── telegram_handlers.py  # Command handlers
    └── telegram_integration.py # File sender
```

## 🔐 လုံခြုံရေး

- Bot token ကို လျှို့ဝှက်ထားပါ
- `config.toml` မျှဝေခြင်း မပြုလုပ်ပါနှင့်
- File size limits သတ်မှတ်ထားပါ
- User sessions သီးခြား ခွဲထားပါသည်

## 🌟 အထူး လုပ်ဆောင်ချက်များ

1. **Dual Mode**: CLI နှင့် Bot နှစ်မျိုးလုံး အလုပ်လုပ်
2. **Multi-User**: တစ်ချိန်တည်းတွင် အသုံးပြုသူ အများအပြား
3. **Auto-Upload**: ဒေါင်းလုဒ်ပြီးသည်နှင့် အလိုအလျောက် ပို့
4. **Rich Metadata**: Cover art, lyrics, tags အပြည့်အစုံ
5. **Progress Updates**: Real-time အကြောင်းကြားချက်များ

## 📊 Performance

- **Async Architecture**: Non-blocking operations
- **Concurrent Downloads**: တစ်ချိန်တည်းတွင် download အများအပြား
- **Task Queue**: အများဆုံး 128 tasks
- **Efficient I/O**: Optimized file operations

## 🆘 အကူအညီ

### Documentation
- [QUICK_START.md](QUICK_START.md) - 5 မိနစ် setup
- [TELEGRAM_BOT_SETUP_MM.md](TELEGRAM_BOT_SETUP_MM.md) - အပြည့်အစုံ လမ်းညွှန်
- [BOT_WORKFLOW.md](BOT_WORKFLOW.md) - Technical details

### Community
- **GitHub**: https://github.com/WorldObservationLog/AppleMusicDecrypt
- **Telegram Group**: https://t.me/apple_music_alac

### Issues
- GitHub Issues တွင် ပြဿနာများ တင်ပြနိုင်ပါသည်
- Telegram Group တွင် မေးမြန်းနိုင်ပါသည်

## 📝 License

AppleMusicDecrypt project license နှင့် တူညီပါသည်။

## 🙏 Credits

- Original Project: [WorldObservationLog/AppleMusicDecrypt](https://github.com/WorldObservationLog/AppleMusicDecrypt)
- Inspired by: [zhaarey/apple-music-alac-atmos-downloader](https://github.com/zhaarey/apple-music-alac-atmos-downloader)
- Telegram Bot Integration: 2025

---

## 🎯 အသုံးပြုမှု ဥပမာ

### သီချင်း တစ်ပုဒ် ဒေါင်းလုဒ်လုပ်ခြင်း
```
/download https://music.apple.com/jp/song/caribbean-blue/339592231
```

### အယ်လ်ဘမ် တစ်ခုလုံး ဒေါင်းလုဒ်လုပ်ခြင်း
```
/dl https://music.apple.com/jp/album/nameless-name-single/1688539265
```

### Codec သတ်မှတ်ခြင်း
```
/download https://music.apple.com/... alac
```

### တိုက်ရိုက် URL ပို့ခြင်း
```
https://music.apple.com/jp/playlist/bocchi-the-rock/pl.u-Ympg5s39LRqp
```

---

**သင့်သီချင်းများကို ပျော်ရွှင်စွာ နားဆင်ပါ! 🎶**
