import asyncio
import sys

from creart import it
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.api import WebAPI
from src.config import Config
from src.grpc.manager import WrapperManager
from src.logger import GlobalLogger
from src.qemu import QemuInstance
from src.telegram_handlers import (
    start_command,
    help_command,
    status_command,
    download_command,
    handle_message
)
from src.utils import check_dep, run_sync


class TelegramBot:
    """Telegram Bot for Apple Music Downloads"""
    
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.application = None
        self.localInstance = QemuInstance()
        
        # Check dependencies
        dep_installed, missing_dep = check_dep()
        if not dep_installed:
            it(GlobalLogger).logger.error(f"Dependence {missing_dep} was not installed!")
            loop.stop()
            sys.exit()
        
        # Check if Telegram bot is enabled
        if not it(Config).telegram.enable:
            it(GlobalLogger).logger.error("Telegram bot is not enabled in config.toml!")
            it(GlobalLogger).logger.error("Please set telegram.enable = true and provide botToken")
            loop.stop()
            sys.exit()
        
        if not it(Config).telegram.botToken or it(Config).telegram.botToken == "YOUR_BOT_TOKEN_HERE":
            it(GlobalLogger).logger.error("Telegram bot token is not configured!")
            it(GlobalLogger).logger.error("Please set telegram.botToken in config.toml")
            loop.stop()
            sys.exit()
    
    async def initialize(self):
        """Initialize bot and services"""
        it(GlobalLogger).logger.info("Initializing Telegram Bot...")
        
        # Initialize WebAPI
        await run_sync(it(WebAPI).init)
        
        # Initialize local instance if enabled
        if it(Config).localInstance.enable:
            await self.localInstance.launch_instance(self.loop)
            it(Config).instance.url = "127.0.0.1:32767"
            it(Config).instance.secure = False
        
        # Initialize WrapperManager
        await it(WrapperManager).init(it(Config).instance.url, it(Config).instance.secure)
        
        # Check wrapper-manager status
        try:
            it(WrapperManager).status.cache_invalidate()
            st_resp = await it(WrapperManager).status()
            if not st_resp.regions:
                it(GlobalLogger).logger.warning(
                    "No available accounts on wrapper-manager instance. "
                    "Users will need to login first."
                )
            else:
                it(GlobalLogger).logger.info(
                    f"Wrapper-manager regions available: {', '.join(st_resp.regions)}"
                )
        except Exception as e:
            it(GlobalLogger).logger.error(f"Unable to connect to wrapper-manager: {e}")
            sys.exit()
        
        # Create Telegram application
        self.application = Application.builder().token(it(Config).telegram.botToken).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("status", status_command))
        self.application.add_handler(CommandHandler("download", download_command))
        self.application.add_handler(CommandHandler("dl", download_command))
        
        # Add message handler for URLs
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        
        it(GlobalLogger).logger.info("✅ Telegram Bot initialized successfully!")
    
    async def start(self):
        """Start the bot"""
        await self.initialize()
        
        it(GlobalLogger).logger.info("🤖 Starting Telegram Bot...")
        it(GlobalLogger).logger.info(f"Bot is ready to receive messages!")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            allowed_updates=["message", "callback_query"]
        )
        
        # Keep the bot running
        try:
            # Run forever
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            it(GlobalLogger).logger.info("Shutting down bot...")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot"""
        it(GlobalLogger).logger.info("Stopping Telegram Bot...")
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        
        if it(Config).localInstance.enable:
            await self.localInstance.terminate()
        
        it(GlobalLogger).logger.info("Bot stopped.")
