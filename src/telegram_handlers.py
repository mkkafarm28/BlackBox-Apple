import os
from typing import Dict, Optional

from creart import it
from telegram import Update
from telegram.ext import ContextTypes

from src.api import WebAPI
from src.config import Config
from src.flags import Flags
from src.grpc.manager import WrapperManager
from src.logger import GlobalLogger
from src.rip import rip_song, rip_album, rip_artist, rip_playlist
from src.telegram_integration import set_telegram_context
from src.url import AppleMusicURL, URLType
from src.utils import safely_create_task

# Store user sessions: chat_id -> user_data
user_sessions: Dict[int, dict] = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    user_sessions[chat_id] = {"downloads": []}
    
    welcome_message = """
🎵 **Apple Music Download Bot**

Welcome! I can help you download music from Apple Music.

**Available Commands:**
/download <url> - Download song/album/playlist
/status - Check wrapper-manager status
/help - Show this help message

**Supported Links:**
• Apple Music Song
• Apple Music Album
• Apple Music Artist
• Apple Music Playlist

**Example:**
`/download https://music.apple.com/jp/album/nameless-name-single/1688539265`

Send me an Apple Music link to get started!
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start_command(update, context)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    try:
        it(WrapperManager).status.cache_invalidate()
        st_resp = await it(WrapperManager).status()
        
        if not st_resp.regions:
            await update.message.reply_text(
                "⚠️ No available accounts on wrapper-manager instance.\n"
                "Please contact the administrator."
            )
        else:
            regions = ', '.join(st_resp.regions)
            await update.message.reply_text(
                f"✅ **Wrapper-Manager Status**\n\n"
                f"Available regions: {regions}",
                parse_mode='Markdown'
            )
    except Exception as e:
        it(GlobalLogger).logger.error(f"Status check failed: {e}")
        await update.message.reply_text(
            "❌ Failed to connect to wrapper-manager.\n"
            "Please try again later."
        )


async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /download command"""
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an Apple Music URL.\n\n"
            "**Usage:** `/download <url>`\n"
            "**Example:** `/download https://music.apple.com/jp/album/nameless-name-single/1688539265`",
            parse_mode='Markdown'
        )
        return
    
    raw_url = context.args[0]
    codec = "alac"  # Default codec
    
    # Check for codec option
    if len(context.args) > 1 and context.args[1] in ["alac", "ec3", "aac", "aac-binaural", "aac-downmix", "aac-legacy", "ac3"]:
        codec = context.args[1]
    
    await update.message.reply_text(f"🔍 Processing URL...\n`{raw_url}`", parse_mode='Markdown')
    
    try:
        url = AppleMusicURL.parse_url(raw_url)
        if not url:
            real_url = await it(WebAPI).get_real_url(raw_url)
            url = AppleMusicURL.parse_url(real_url)
            if not url:
                await update.message.reply_text("❌ Invalid Apple Music URL!")
                return
        
        # Store chat_id in context for progress updates
        flags = Flags(force_save=False, language=it(Config).region.language)
        
        # Store the Telegram context for this download
        if chat_id not in user_sessions:
            user_sessions[chat_id] = {}
        user_sessions[chat_id]['chat_id'] = chat_id
        user_sessions[chat_id]['context'] = context
        user_sessions[chat_id]['url_id'] = url.id
        
        # Set Telegram context for the download task
        set_telegram_context(url.id, chat_id, context)
        
        if url.type == URLType.Song:
            await update.message.reply_text("🎵 Downloading song...")
            safely_create_task(rip_song(url, codec, flags))
        elif url.type == URLType.Album:
            await update.message.reply_text("💿 Downloading album...")
            safely_create_task(rip_album(url, codec, flags))
        elif url.type == URLType.Artist:
            await update.message.reply_text("👤 Downloading artist's albums...")
            safely_create_task(rip_artist(url, codec, flags))
        elif url.type == URLType.Playlist:
            await update.message.reply_text("📋 Downloading playlist...")
            safely_create_task(rip_playlist(url, codec, flags))
        else:
            await update.message.reply_text("❌ Unsupported URL type!")
            return
        
        await update.message.reply_text(
            "⏳ Download started! You'll receive the file(s) when ready.\n"
            "This may take a few minutes depending on the size."
        )
        
    except Exception as e:
        it(GlobalLogger).logger.error(f"Download failed: {e}")
        await update.message.reply_text(f"❌ Download failed: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (URLs without command)"""
    text = update.message.text.strip()
    
    # Check if it's an Apple Music URL
    if "music.apple.com" in text:
        # Treat it as a download command
        context.args = [text]
        await download_command(update, context)
    else:
        await update.message.reply_text(
            "Please send an Apple Music URL or use /help to see available commands."
        )


async def send_file_to_user(chat_id: int, file_path: str, caption: str, context: ContextTypes.DEFAULT_TYPE):
    """Send downloaded file to user"""
    try:
        if not os.path.exists(file_path):
            it(GlobalLogger).logger.error(f"File not found: {file_path}")
            return
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        max_size = it(Config).telegram.maxFileSize
        
        if file_size_mb > max_size:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ File is too large ({file_size_mb:.1f}MB > {max_size}MB)\n"
                     f"File saved at: `{file_path}`",
                parse_mode='Markdown'
            )
            return
        
        # Send as audio file
        with open(file_path, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                caption=caption,
                read_timeout=300,
                write_timeout=300
            )
        
        it(GlobalLogger).logger.info(f"File sent to user {chat_id}: {file_path}")
        
    except Exception as e:
        it(GlobalLogger).logger.error(f"Failed to send file: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Failed to send file: {str(e)}\n"
                 f"File saved at: `{file_path}`",
            parse_mode='Markdown'
        )


def get_user_context(chat_id: int) -> Optional[dict]:
    """Get user session context"""
    return user_sessions.get(chat_id)
