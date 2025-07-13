"""
Telegram Userbot Manager
Handles Telegram client initialization and message processing
"""

import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import User, Channel, Chat

from command_handler import CommandHandler
from forwarding_engine import ForwardingEngine
from replacement_engine import ReplacementEngine
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class TelegramUserbot:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient('session', api_id, api_hash)

        # Initialize components
        self.config_manager = ConfigManager()
        self.forwarding_engine = ForwardingEngine(self.client, self.config_manager)
        self.replacement_engine = ReplacementEngine(self.config_manager)
        self.command_handler = CommandHandler(
            self.client,
            self.forwarding_engine,
            self.replacement_engine,
            self.config_manager
        )

        # Register event handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register message event handlers"""

        @self.client.on(events.NewMessage(pattern=r'^/'))
        async def handle_command(event):
            """Handle command messages"""
            try:
                await self.command_handler.handle_command(event)
            except Exception as e:
                logger.error(f"Command handling error: {e}")
                await event.reply(f"❌ Error: {e}")

        @self.client.on(events.NewMessage())
        async def handle_message(event):
            """Handle regular messages for forwarding"""
            try:
                if event.message.text and event.message.text.startswith('/'):
                    return

                await self.forwarding_engine.process_message(event)

            except Exception as e:
                logger.error(f"Message processing error: {e}")

        @self.client.on(events.MessageEdited())
        async def handle_edited_message(event):
            """Handle edited messages"""
            try:
                await self.forwarding_engine.process_edited_message(event)
            except Exception as e:
                logger.error(f"Edited message processing error: {e}")

    async def start(self):
        """Start the Telegram client"""
        try:
            await self.client.start()

            me = await self.client.get_me()
            logger.info(f"✅ Logged in as: {me.username} ({me.id})")

            await self.config_manager.load_config()
            await self.forwarding_engine.start()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start userbot: {e}")
            raise

    async def run_forever(self):
        """Keep the bot running"""
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("🛑 Userbot stopped by user")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            raise
        finally:
            await self.forwarding_engine.stop()
            await self.config_manager.save_config()

    async def stop(self):
        """Stop the userbot"""
        try:
            await self.forwarding_engine.stop()
            await self.config_manager.save_config()
            await self.client.disconnect()
            logger.info("✅ Userbot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping userbot: {e}")
