# Telegram Bot တပ်ဆင်ခြင်း လမ်းညွှန်

Apple Music Download Telegram Bot ကို တပ်ဆင်ရန် လမ်းညွှန်ချက်များ

## လိုအပ်သော အရာများ

1. Python 3.11 သို့မဟုత် ပိုမြင့်သော ဗားရှင်း
2. Poetry (Python package manager)
3. [@BotFather](https://t.me/BotFather) မှ Telegram Bot Token

## အဆင့် ၁ - Telegram Bot ဖန်တီးခြင်း

1. Telegram တွင် [@BotFather](https://t.me/BotFather) ကို ရှာပါ
2. `/newbot` command ပို့ပါ
3. လမ်းညွှန်ချက်များအတိုင်း လုပ်ဆောင်ပါ
4. Bot token ကို မှတ်သားထားပါ (ဥပမာ: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## အဆင့် ၂ - Configuration ပြင်ဆင်ခြင်း

1. Example configuration ကို ကူးယူပါ:
   ```bash
   cp config.example.toml config.toml
   ```

2. `config.toml` ဖိုင်ကို ဖွင့်ပြီး Telegram section ကို ပြင်ဆင်ပါ:
   ```toml
   [telegram]
   botToken = "YOUR_BOT_TOKEN_HERE"  # သင့် bot token ကို ထည့်ပါ
   enable = true                      # Telegram bot mode ကို ဖွင့်ပါ
   maxFileSize = 50                   # အများဆုံး file size (MB)
   ```

3. Wrapper-manager instance ကို ပြင်ဆင်ပါ:
   ```toml
   [instance]
   url = "wm.wol.moe"  # သို့မဟုత် သင့်ကိုယ်ပိုင် wrapper-manager
   secure = true
   ```

## အဆင့် ၃ - Dependencies များ ထည့်သွင်းခြင်း

```bash
# System dependencies များ ထည့်သွင်းပါ (လိုအပ်ပါက)
bash ./tools/install-deps.sh

# Python dependencies များ ထည့်သွင်းပါ
poetry install
```

## အဆင့် ၄ - Bot ကို စတင်ခြင်း

```bash
poetry run python telegram_main.py
```

အောက်ပါအတိုင်း မြင်ရပါမည်:
```
✅ Telegram Bot initialized successfully!
🤖 Starting Telegram Bot...
Bot is ready to receive messages!
```

## အဆင့် ၅ - Bot ကို အသုံးပြုခြင်း

1. Telegram တွင် သင့် bot ကို username ဖြင့် ရှာပါ
2. `/start` ပို့ပြီး စတင်ပါ
3. Apple Music URL ပို့ပါ သို့မဟုత် `/download <url>` သုံးပါ

### အသုံးပြုနိုင်သော Commands များ

- `/start` - ကြိုဆိုစာနှင့် အကူအညီ ပြသခြင်း
- `/help` - အသုံးပြုနိုင်သော commands များ ပြသခြင်း
- `/download <url>` - Apple Music မှ သီချင်း/အယ်လ်ဘမ်/playlist ဒေါင်းလုဒ်လုပ်ခြင်း
- `/dl <url>` - Download command ၏ အတိုကောက်
- `/status` - Wrapper-manager အခြေအနေ စစ်ဆေးခြင်း

### အသုံးပြုနိုင်သော URLs များ

- Apple Music သီချင်း: `https://music.apple.com/jp/song/caribbean-blue/339592231`
- Apple Music အယ်လ်ဘမ်: `https://music.apple.com/jp/album/nameless-name-single/1688539265`
- Apple Music အနုပညာရှင်: `https://music.apple.com/jp/artist/...`
- Apple Music Playlist: `https://music.apple.com/jp/playlist/...`

### Download ရွေးချယ်စရာများ

URL နောက်တွင် codec ကို သတ်မှတ်နိုင်ပါသည်:
```
/download https://music.apple.com/... alac
/download https://music.apple.com/... aac
/download https://music.apple.com/... ec3
```

အသုံးပြုနိုင်သော codecs: `alac`, `ec3`, `ac3`, `aac`, `aac-binaural`, `aac-downmix`, `aac-legacy`

## လုပ်ဆောင်ချက်များ

✅ သီချင်း၊ အယ်လ်ဘမ်၊ အနုပညာရှင်နှင့် playlists များ ဒေါင်းလုဒ်လုပ်ခြင်း  
✅ Codec အမျိုးမျိုး ပံ့ပိုးမှု (ALAC, AAC, EC3, AC3)  
✅ Telegram သို့ အလိုအလျောက် file upload လုပ်ခြင်း  
✅ Progress အကြောင်းကြားချက်များ  
✅ Metadata ထည့်သွင်းခြင်း (ခေါင်းစဉ်၊ အနုပညာရှင်၊ အယ်လ်ဘမ်၊ cover art)  
✅ သီချင်းစာသား ပံ့ပိုးမှု (.lrc files)  
✅ အသုံးပြုသူ အများအပြား ပံ့ပိုးမှု  

## ပြဿနာ ဖြေရှင်းခြင်း

### Bot က တုံ့ပြန်မှု မရှိပါက
- `config.toml` တွင် bot token မှန်ကန်မှု စစ်ဆေးပါ
- `telegram.enable = true` ဖြစ်မှန်း သေချာပါစေ
- Console တွင် error messages များ စစ်ဆေးပါ

### "Unable to connect to wrapper-manager"
- Internet ချိတ်ဆက်မှု စစ်ဆေးပါ
- Config တွင် wrapper-manager URL မှန်ကန်မှု စစ်ဆေးပါ
- Public instance အသုံးပြုကြည့်ပါ: `wm.wol.moe`

### Files များ အရွယ်အစား ကြီးလွန်းပါက
- Config တွင် `maxFileSize` တိုးမြှင့်ပါ (Telegram limit မှာ bots အတွက် 50MB)
- Limit ထက် ကြီးသော files များကို local တွင်သာ သိမ်းဆည်းမည်

### Download မအောင်မြင်ပါက
- Apple Music URL မှန်ကန်မှု စစ်ဆေးပါ
- Wrapper-manager တွင် accounts များ ရှိမရှိ စစ်ဆေးပါ (`/status` command)
- Console logs များတွင် အသေးစိတ် error messages များ ကြည့်ပါ

## လုံခြုံရေး မှတ်ချက်များ

- Bot token ကို လျှို့ဝှက်ထားပါ
- `config.toml` ဖိုင်ကို မျှဝေခြင်း မပြုလုပ်ပါနှင့်
- လိုအပ်ပါက bot ကို သတ်မှတ်ထားသော အသုံးပြုသူများသာ အသုံးပြုနိုင်အောင် ကန့်သတ်ပါ
- Files များကို `downloads/` directory တွင် local သိမ်းဆည်းပါသည်

## အကူအညီ

ပြဿနာများနှင့် မေးခွန်းများအတွက်:
- GitHub Issues: https://github.com/WorldObservationLog/AppleMusicDecrypt/issues
- Telegram Group: https://t.me/apple_music_alac

## License

AppleMusicDecrypt project license နှင့် တူညီပါသည်။
