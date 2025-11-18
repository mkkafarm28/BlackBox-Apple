import asyncio
import os
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from creart import it

from src.api import WebAPI
from src.config import Config
from src.flags import Flags
from src.grpc.manager import WrapperManager, WrapperManagerException
from src.logger import GlobalLogger
from src.rip import rip_song, rip_album, rip_artist, rip_playlist
from src.url import AppleMusicURL, URLType
from src.user_sessions import UserSessionManager
from src.utils import safely_create_task


class TelegramBot:
    """Telegram bot for Apple Music downloads"""
    
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.config = it(Config)
        self.session_manager = UserSessionManager()
        self.application: Optional[Application] = None
        self.download_tasks = {}  # Track download tasks per user
        
        # Create temp directory if it doesn't exist
        self.temp_dir = Path(self.config.telegram.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        welcome_message = (
            "🎵 *Apple Music Download Bot*\n\n"
            "Welcome! I can help you download music from Apple Music.\n\n"
            "*Commands:*\n"
            "/login - Login with your Apple Music account\n"
            "/logout - Logout from your account\n"
            "/status - Check wrapper-manager status\n"
            "/help - Show this help message\n\n"
            "*Usage:*\n"
            "1. First, use /login to authenticate\n"
            "2. Send me any Apple Music URL (song, album, playlist, or artist)\n"
            "3. I'll download and send you the files!\n\n"
            "*Supported URLs:*\n"
            "• Songs\n"
            "• Albums\n"
            "• Playlists\n"
            "• Artists (all albums)\n\n"
            "*Supported Codecs:*\n"
            "ALAC, EC3 (Atmos), AC3, AAC, AAC-Binaural, AAC-Downmix"
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start_command(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            it(WrapperManager).status.cache_invalidate()
            st_resp = await it(WrapperManager).status()
            
            if not st_resp.regions:
                await update.message.reply_text(
                    "⚠️ No available accounts on wrapper-manager.\n"
                    "Please use /login to authenticate."
                )
            else:
                regions = ', '.join(st_resp.regions)
                await update.message.reply_text(
                    f"✅ *Wrapper-Manager Status*\n\n"
                    f"Available regions: {regions}",
                    parse_mode='Markdown'
                )
        except Exception as e:
            it(GlobalLogger).logger.error(f"Status check failed: {e}")
            await update.message.reply_text(
                "❌ Failed to check status. Please try again later."
            )
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /login command"""
        user_id = update.effective_user.id
        
        # Check if already authenticated
        if await self.session_manager.is_authenticated(user_id):
            await update.message.reply_text(
                "✅ You are already logged in!\n"
                "Use /logout to logout first if you want to login with a different account."
            )
            return
        
        await update.message.reply_text(
            "🔐 *Login Process*\n\n"
            "Please send your Apple ID (email):",
            parse_mode='Markdown'
        )
        
        # Mark user as awaiting username
        session = await self.session_manager.get_session(user_id)
        await self.session_manager.update_session(user_id, awaiting_password=False, awaiting_2fa=False)
    
    async def logout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logout command"""
        user_id = update.effective_user.id
        session = await self.session_manager.get_session(user_id)
        
        if not session.is_authenticated:
            await update.message.reply_text("ℹ️ You are not logged in.")
            return
        
        try:
            # Logout from wrapper-manager
            if session.username:
                await it(WrapperManager).logout(session.username)
            
            # Clear local session
            await self.session_manager.clear_session(user_id)
            
            await update.message.reply_text("✅ Successfully logged out!")
            it(GlobalLogger).logger.info(f"User {user_id} logged out")
        except WrapperManagerException as e:
            it(GlobalLogger).logger.error(f"Logout failed for user {user_id}: {e}")
            await update.message.reply_text(
                "⚠️ Logout from wrapper-manager failed, but local session cleared."
            )
            await self.session_manager.clear_session(user_id)
    
    async def handle_2fa_callback(self, user_id: int, username: str, password: str) -> str:
        """Callback for 2FA code input"""
        # Mark user as awaiting 2FA
        await self.session_manager.set_awaiting_2fa(user_id)
        
        # Wait for 2FA code (will be provided via message handler)
        session = await self.session_manager.get_session(user_id)
        
        # Wait up to 5 minutes for 2FA code
        for _ in range(300):  # 300 seconds = 5 minutes
            await asyncio.sleep(1)
            session = await self.session_manager.get_session(user_id)
            if hasattr(session, 'two_fa_code') and session.two_fa_code:
                code = session.two_fa_code
                # Clear the code
                await self.session_manager.update_session(user_id, two_fa_code=None)
                return code
        
        raise TimeoutError("2FA code not provided within 5 minutes")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        session = await self.session_manager.get_session(user_id)
        
        # Handle login flow
        if not session.is_authenticated:
            # Awaiting username
            if not session.temp_username and not session.awaiting_password and not session.awaiting_2fa:
                await self.session_manager.start_login(user_id, text)
                await update.message.reply_text(
                    "🔑 Now send your password:\n"
                    "(Your password will be deleted immediately after processing)"
                )
                return
            
            # Awaiting password
            if session.awaiting_password and session.temp_username:
                password = text
                # Delete the password message for security
                try:
                    await update.message.delete()
                except:
                    pass
                
                await self.session_manager.set_password(user_id, password)
                await update.message.reply_text("🔄 Logging in...")
                
                # Attempt login
                try:
                    # Create a 2FA callback that will wait for user input
                    async def on_2fa(username: str, password: str):
                        await self.session_manager.set_awaiting_2fa(user_id)
                        await context.bot.send_message(
                            chat_id=user_id,
                            text="🔐 Two-factor authentication required.\n"
                                 "Please send your 2FA code:"
                        )
                        
                        # Wait for 2FA code
                        for _ in range(300):  # 5 minutes timeout
                            await asyncio.sleep(1)
                            current_session = await self.session_manager.get_session(user_id)
                            if hasattr(current_session, 'two_fa_code') and current_session.two_fa_code:
                                code = current_session.two_fa_code
                                await self.session_manager.update_session(user_id, two_fa_code=None)
                                return code
                        raise TimeoutError("2FA code timeout")
                    
                    await it(WrapperManager).login(session.temp_username, password, on_2fa)
                    
                    # Login successful
                    await self.session_manager.set_authenticated(user_id, session.temp_username)
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="✅ Login successful!\n\n"
                             "You can now send Apple Music URLs to download."
                    )
                    it(GlobalLogger).logger.info(f"User {user_id} logged in as {session.temp_username}")
                    
                except WrapperManagerException as e:
                    it(GlobalLogger).logger.error(f"Login failed for user {user_id}: {e}")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ Login failed. Please check your credentials and try again with /login"
                    )
                    await self.session_manager.clear_session(user_id)
                except Exception as e:
                    it(GlobalLogger).logger.error(f"Login error for user {user_id}: {e}")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ An error occurred during login. Please try again with /login"
                    )
                    await self.session_manager.clear_session(user_id)
                return
            
            # Awaiting 2FA code
            if session.awaiting_2fa:
                await self.session_manager.update_session(user_id, two_fa_code=text, awaiting_2fa=False)
                return
            
            # Not logged in and not in login flow
            await update.message.reply_text(
                "⚠️ Please login first using /login command."
            )
            return
        
        # User is authenticated, check if message is an Apple Music URL
        url = AppleMusicURL.parse_url(text)
        if not url:
            # Try to get real URL
            try:
                real_url = await it(WebAPI).get_real_url(text)
                url = AppleMusicURL.parse_url(real_url)
            except:
                pass
        
        if not url:
            await update.message.reply_text(
                "❌ Invalid Apple Music URL.\n\n"
                "Please send a valid Apple Music link for:\n"
                "• Song\n"
                "• Album\n"
                "• Playlist\n"
                "• Artist"
            )
            return
        
        # Start download
        await self.handle_download(update, context, url)
    
    async def handle_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: AppleMusicURL):
        """Handle download request"""
        user_id = update.effective_user.id
        codec = "alac"  # Default codec
        
        # Send initial message
        type_name = url.type.name
        await update.message.reply_text(
            f"📥 Starting download...\n"
            f"Type: {type_name}\n"
            f"Codec: {codec.upper()}"
        )
        
        try:
            flags = Flags(force_save=False, language=self.config.region.language)
            
            # Start appropriate rip task based on URL type
            match url.type:
                case URLType.Song:
                    safely_create_task(self.download_and_send(user_id, url, codec, flags, update, context))
                case URLType.Album:
                    await update.message.reply_text(
                        "📀 Downloading album... This may take a while."
                    )
                    safely_create_task(self.download_album(user_id, url, codec, flags, update, context))
                case URLType.Artist:
                    await update.message.reply_text(
                        "👤 Downloading artist's albums... This may take a while."
                    )
                    safely_create_task(self.download_artist(user_id, url, codec, flags, update, context))
                case URLType.Playlist:
                    await update.message.reply_text(
                        "📝 Downloading playlist... This may take a while."
                    )
                    safely_create_task(self.download_playlist(user_id, url, codec, flags, update, context))
                case _:
                    await update.message.reply_text("❌ Unsupported URL type")
        
        except Exception as e:
            it(GlobalLogger).logger.error(f"Download error for user {user_id}: {e}")
            await update.message.reply_text(
                f"❌ Download failed: {str(e)}"
            )
    
    async def download_and_send(self, user_id: int, url, codec: str, flags: Flags, 
                                update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Download a single song and send to user"""
        try:
            # Trigger the download
            await rip_song(url, codec, flags)
            
            # Wait a bit for the file to be saved
            await asyncio.sleep(2)
            
            # Find the downloaded file
            # Note: This is a simplified approach. In production, you'd want to track
            # the exact file path from the rip_song function
            downloads_dir = Path(self.config.download.dirPathFormat.split('/')[0])
            
            # Search for recently created files
            if downloads_dir.exists():
                files = sorted(downloads_dir.rglob('*.*'), key=lambda p: p.stat().st_mtime, reverse=True)
                
                # Send the most recent file (assuming it's our download)
                if files:
                    file_path = files[0]
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    if file_size_mb > self.config.telegram.max_file_size:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"❌ File too large ({file_size_mb:.1f}MB). "
                                 f"Telegram limit is {self.config.telegram.max_file_size}MB."
                        )
                        return
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"📤 Uploading: {file_path.name}"
                    )
                    
                    with open(file_path, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=user_id,
                            document=f,
                            filename=file_path.name,
                            caption="✅ Download complete!"
                        )
                    
                    it(GlobalLogger).logger.info(f"Sent file to user {user_id}: {file_path.name}")
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ Download completed but file not found."
                    )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Downloads directory not found."
                )
        
        except Exception as e:
            it(GlobalLogger).logger.error(f"Error sending file to user {user_id}: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Error: {str(e)}"
            )
    
    async def download_album(self, user_id: int, url, codec: str, flags: Flags,
                            update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Download an album"""
        try:
            await rip_album(url, codec, flags)
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Album download completed!\n"
                     "Note: Files are saved to the downloads directory."
            )
        except Exception as e:
            it(GlobalLogger).logger.error(f"Album download error: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Album download failed: {str(e)}"
            )
    
    async def download_artist(self, user_id: int, url, codec: str, flags: Flags,
                             update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Download artist's albums"""
        try:
            await rip_artist(url, codec, flags)
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Artist download completed!\n"
                     "Note: Files are saved to the downloads directory."
            )
        except Exception as e:
            it(GlobalLogger).logger.error(f"Artist download error: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Artist download failed: {str(e)}"
            )
    
    async def download_playlist(self, user_id: int, url, codec: str, flags: Flags,
                               update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Download a playlist"""
        try:
            await rip_playlist(url, codec, flags)
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Playlist download completed!\n"
                     "Note: Files are saved to the downloads directory."
            )
        except Exception as e:
            it(GlobalLogger).logger.error(f"Playlist download error: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Playlist download failed: {str(e)}"
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        it(GlobalLogger).logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later."
            )
    
    async def start(self):
        """Start the Telegram bot"""
        if not self.config.telegram.bot_token:
            it(GlobalLogger).logger.error("Telegram bot token not configured!")
            return
        
        # Build application
        self.application = Application.builder().token(self.config.telegram.bot_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("login", self.login_command))
        self.application.add_handler(CommandHandler("logout", self.logout_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        it(GlobalLogger).logger.info("Starting Telegram bot...")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        it(GlobalLogger).logger.info("Telegram bot is running!")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            it(GlobalLogger).logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
