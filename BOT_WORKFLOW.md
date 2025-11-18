# Telegram Bot Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram User                            │
│                  (Sends Apple Music URL)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              telegram_main.py (Entry Point)                  │
│  • Initializes all services                                  │
│  • Creates event loop                                        │
│  • Starts bot                                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           src/telegram_bot.py (Bot Manager)                  │
│  • Manages bot lifecycle                                     │
│  • Registers command handlers                                │
│  • Connects to Telegram API                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        src/telegram_handlers.py (Command Handlers)           │
│  • /start → Welcome message                                  │
│  • /download → Parse URL & start download                    │
│  • /status → Check wrapper-manager                           │
│  • Direct URL → Auto-download                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              src/rip.py (Download Engine)                    │
│  • Parse Apple Music URL                                     │
│  • Fetch metadata                                            │
│  • Download encrypted stream                                 │
│  • Decrypt audio                                             │
│  • Encapsulate & write metadata                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              src/save.py (File Saver)                        │
│  • Save audio file locally                                   │
│  • Save cover art                                            │
│  • Save lyrics (.lrc)                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      src/telegram_integration.py (Telegram Sender)           │
│  • Check file size                                           │
│  • Prepare metadata caption                                  │
│  • Upload to Telegram                                        │
│  • Send completion message                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Telegram User                            │
│                  (Receives Audio File)                       │
└─────────────────────────────────────────────────────────────┘
```

## Message Flow

### 1. User Sends URL
```
User → Telegram → Bot Handler
```

### 2. URL Processing
```
Bot Handler → URL Parser → Content Type Detection
                          ├─ Song
                          ├─ Album
                          ├─ Artist
                          └─ Playlist
```

### 3. Download Process
```
Download Engine → Apple Music API → Metadata
                → CDN → Encrypted Stream
                → Wrapper-Manager → Decryption
                → MP4 Processor → Final Audio
```

### 4. File Delivery
```
Local Save → Telegram Integration → File Upload → User
```

## State Management

```
┌──────────────────────────────────────────────────────┐
│              User Session Storage                     │
│  {                                                    │
│    chat_id: 123456789,                               │
│    context: TelegramContext,                         │
│    url_id: "song_id_12345",                          │
│    downloads: [...]                                  │
│  }                                                    │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│           Telegram Context Mapping                    │
│  {                                                    │
│    "song_id_12345": {                                │
│      chat_id: 123456789,                             │
│      context: TelegramContext                        │
│    }                                                  │
│  }                                                    │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│              Task Tracking                            │
│  adam_id_task_mapping[song_id] = Task                │
│  • Status: PENDING → DOWNLOADING → DECRYPTING        │
│           → SAVING → DONE                            │
└──────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
Error Occurs
    │
    ├─ Network Error → Retry Logic → User Notification
    │
    ├─ Invalid URL → Immediate User Notification
    │
    ├─ File Too Large → Skip Upload → Notify Local Path
    │
    ├─ Wrapper Error → Retry → User Notification
    │
    └─ Unknown Error → Log → User Notification
```

## Configuration Flow

```
config.toml
    │
    ├─ [telegram]
    │   ├─ botToken → Bot Authentication
    │   ├─ enable → Feature Toggle
    │   └─ maxFileSize → Upload Limit
    │
    ├─ [instance]
    │   ├─ url → Wrapper-Manager Address
    │   └─ secure → HTTPS/HTTP
    │
    ├─ [download]
    │   ├─ codecPriority → Quality Selection
    │   ├─ dirPathFormat → Save Location
    │   └─ saveLyrics → Feature Toggle
    │
    └─ [metadata]
        └─ embedMetadata → Tags to Include
```

## Concurrent Operations

```
User A → /download URL1 ─┐
                          │
User B → /download URL2 ─┼─→ Task Queue → Parallel Processing
                          │              (maxRunningTasks: 128)
User C → /download URL3 ─┘
                          │
                          ├─→ Task 1 → Download → Decrypt → Save → Upload A
                          ├─→ Task 2 → Download → Decrypt → Save → Upload B
                          └─→ Task 3 → Download → Decrypt → Save → Upload C
```

## Security Layers

```
┌─────────────────────────────────────────────────────┐
│  1. Telegram API Authentication (Bot Token)          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  2. Wrapper-Manager Connection (Secure/Insecure)     │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  3. File Size Validation (maxFileSize)               │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  4. Local File System (downloads/ directory)         │
└─────────────────────────────────────────────────────┘
```

## Performance Optimization

```
┌─────────────────────────────────────────────────────┐
│  Async/Await Architecture                            │
│  • Non-blocking I/O                                  │
│  • Concurrent downloads                              │
│  • Parallel decryption                               │
└─────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  Task Semaphore (maxRunningTasks: 128)              │
│  • Prevents resource exhaustion                      │
│  • Manages concurrent operations                     │
└─────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  Caching & Optimization                              │
│  • Metadata caching                                  │
│  • Connection pooling                                │
│  • Efficient file I/O                                │
└─────────────────────────────────────────────────────┘
```

## Monitoring & Logging

```
┌─────────────────────────────────────────────────────┐
│  GlobalLogger (Loguru)                               │
│  • Info: Normal operations                           │
│  • Warning: Non-critical issues                      │
│  • Error: Failures & exceptions                      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  Measurer                                            │
│  • Download speed                                    │
│  • Decrypt speed                                     │
│  • Active tasks count                                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  Console Output                                      │
│  • Real-time status                                  │
│  • Error messages                                    │
│  • Performance metrics                               │
└─────────────────────────────────────────────────────┘
```

---

**Legend:**
- `→` : Data flow
- `├─` : Branch/Option
- `▼` : Sequential step
- `┌─┐` : Component/Module
