"""
Telegram integration module for sending files and progress updates
"""
import asyncio
import os
from typing import Optional

from creart import it

from src.config import Config
from src.logger import GlobalLogger
from src.metadata import SongMetadata


# Global storage for Telegram contexts
telegram_contexts = {}


def set_telegram_context(adam_id: str, chat_id: int, context):
    """Store Telegram context for a download task"""
    telegram_contexts[adam_id] = {
        'chat_id': chat_id,
        'context': context
    }


def get_telegram_context(adam_id: str) -> Optional[dict]:
    """Get Telegram context for a download task"""
    return telegram_contexts.get(adam_id)


def clear_telegram_context(adam_id: str):
    """Clear Telegram context after task completion"""
    if adam_id in telegram_contexts:
        del telegram_contexts[adam_id]


async def send_telegram_file(adam_id: str, file_path: str, metadata: SongMetadata):
    """Send downloaded file to Telegram user"""
    context_data = get_telegram_context(adam_id)
    
    if not context_data:
        # No Telegram context, skip sending
        return
    
    chat_id = context_data['chat_id']
    context = context_data['context']
    
    try:
        if not os.path.exists(file_path):
            it(GlobalLogger).logger.error(f"File not found: {file_path}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ File not found: {file_path}"
            )
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
            clear_telegram_context(adam_id)
            return
        
        # Prepare caption
        caption = f"🎵 **{metadata.title}**\n"
        if metadata.artist:
            caption += f"👤 {metadata.artist}\n"
        if metadata.album:
            caption += f"💿 {metadata.album}\n"
        
        # Send as audio file
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📤 Uploading file ({file_size_mb:.1f}MB)..."
        )
        
        with open(file_path, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                caption=caption,
                title=metadata.title,
                performer=metadata.artist,
                read_timeout=300,
                write_timeout=300,
                parse_mode='Markdown'
            )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Download complete!"
        )
        
        it(GlobalLogger).logger.info(f"File sent to Telegram user {chat_id}: {file_path}")
        
    except Exception as e:
        it(GlobalLogger).logger.error(f"Failed to send file to Telegram: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Failed to send file: {str(e)}\n"
                     f"File saved at: `{file_path}`",
                parse_mode='Markdown'
            )
        except:
            pass
    finally:
        clear_telegram_context(adam_id)


async def send_telegram_progress(adam_id: str, message: str):
    """Send progress update to Telegram user"""
    context_data = get_telegram_context(adam_id)
    
    if not context_data:
        return
    
    chat_id = context_data['chat_id']
    context = context_data['context']
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        it(GlobalLogger).logger.error(f"Failed to send progress to Telegram: {e}")


async def send_telegram_error(adam_id: str, error_message: str):
    """Send error message to Telegram user"""
    context_data = get_telegram_context(adam_id)
    
    if not context_data:
        return
    
    chat_id = context_data['chat_id']
    context = context_data['context']
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ **Error**\n\n{error_message}",
            parse_mode='Markdown'
        )
    except Exception as e:
        it(GlobalLogger).logger.error(f"Failed to send error to Telegram: {e}")
    finally:
        clear_telegram_context(adam_id)
