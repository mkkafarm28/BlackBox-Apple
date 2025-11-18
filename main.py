import asyncio
import argparse
import sys

from creart import add_creator, it

loop = asyncio.new_event_loop()

from src.logger import LoggerCreator
add_creator(LoggerCreator)
from src.config import ConfigCreator
add_creator(ConfigCreator)
from src.api import APICreator
add_creator(APICreator)
from src.grpc.manager import WMCreator
add_creator(WMCreator)
from src.measurer import MeasurerCreator
add_creator(MeasurerCreator)

from src.cmd import InteractiveShell
from src.telegram_bot import TelegramBot
from src.config import Config
from src.logger import GlobalLogger

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Apple Music Decrypt Tool')
    parser.add_argument('--telegram', action='store_true', 
                       help='Run as Telegram bot instead of CLI')
    args = parser.parse_args()
    
    if args.telegram:
        # Run as Telegram bot
        if not it(Config).telegram.bot_token:
            it(GlobalLogger).logger.error(
                "Telegram bot token not configured!\n"
                "Please set 'bot_token' in the [telegram] section of config.toml"
            )
            sys.exit(1)
        
        it(GlobalLogger).logger.info("Starting in Telegram Bot mode...")
        bot = TelegramBot(loop)
        try:
            loop.run_until_complete(bot.start())
        except KeyboardInterrupt:
            it(GlobalLogger).logger.info("Telegram bot stopped by user")
            loop.stop()
    else:
        # Run as CLI
        it(GlobalLogger).logger.info("Starting in CLI mode...")
        cmd = InteractiveShell(loop)
        try:
            loop.run_until_complete(cmd.start())
        except KeyboardInterrupt:
            loop.stop()
