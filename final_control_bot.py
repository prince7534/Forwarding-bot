#!/usr/bin/env python3
"""
Final Control Bot - Works with environment variables
"""

import asyncio
import os
from telethon import TelegramClient, events
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables
os.environ['API_ID'] = '23752062'
os.environ['API_HASH'] = 'd263514cba2e798b082917ffb62393cc'
os.environ['BOT_TOKEN'] = '7712013081:AAFAih65WsuppiCf0bI6JLCc3T-JgG1xfwU'

class FinalControlBot:
    def __init__(self):
        self.api_id = int(os.environ['API_ID'])
        self.api_hash = os.environ['API_HASH']
        self.bot_token = os.environ['BOT_TOKEN']

        # Create bot client
        self.bot = TelegramClient('final_control_bot', self.api_id, self.api_hash)

        # Create userbot client for sending commands
        self.userbot = TelegramClient('userbot_control', self.api_id, self.api_hash)

        self.authorized_users = set()

    async def start(self):
        """Start both clients"""
        try:
            # Start bot
            await self.bot.start(bot_token=self.bot_token)
            bot_me = await self.bot.get_me()
            print(f"✅ Control Bot: @{bot_me.username}")

            # Start userbot
            await self.userbot.start()
            userbot_me = await self.userbot.get_me()
            print(f"✅ Connected to userbot: @{userbot_me.username}")

            # Register handlers
            self.register_handlers()

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def register_handlers(self):
        """Register all bot handlers"""

        @self.bot.on(events.NewMessage(pattern='/start'))
        async def start_cmd(event):
            user = await event.get_sender()
            self.authorized_users.add(user.id)

            await event.reply(
                f"🤖 **Userbot Control Panel**\n\n"
                f"आपका control bot ready है!\n\n"
                f"**Commands:**\n"
                f"• `/add_forward task1 123456 -> 654321` - Forwarding add करें\n"
                f"• `/start_forward task1` - Forwarding start करें\n"
                f"• `/stop_forward task1` - Forwarding stop करें\n"
                f"• `/list_forward` - सभी forwarding rules देखें\n"
                f"• `/add_replace re1 black -> white` - Text replacement\n"
                f"• `/list_replace` - सभी replacements देखें\n"
                f"• `/get_channels` - Channel list देखें\n"
                f"• `/userbot_status` - Status check करें"
            )

        @self.bot.on(events.NewMessage(pattern='/add_forward'))
        async def add_forward_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                text = event.message.text.replace('/add_forward ', '')
                if '->' not in text:
                    await event.reply("❌ Format: `/add_forward task1 123456 -> 654321`")
                    return

                await self.userbot.send_message('me', f"/forward add {text}")
                await event.reply("✅ Forwarding rule added!")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/start_forward'))
        async def start_forward_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                label = event.message.text.replace('/start_forward ', '')
                if not label:
                    await event.reply("❌ Format: `/start_forward task1`")
                    return

                await self.userbot.send_message('me', f"/forward start {label}")
                await event.reply(f"▶️ Started: {label}")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/stop_forward'))
        async def stop_forward_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                label = event.message.text.replace('/stop_forward ', '')
                if not label:
                    await event.reply("❌ Format: `/stop_forward task1`")
                    return

                await self.userbot.send_message('me', f"/forward stop {label}")
                await event.reply(f"⏹️ Stopped: {label}")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/list_forward'))
        async def list_forward_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                await self.userbot.send_message('me', "/forward task")
                await event.reply("📋 Forwarding list आपके userbot में check करें!")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/add_replace'))
        async def add_replace_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                text = event.message.text.replace('/add_replace ', '')
                if '->' not in text:
                    await event.reply("❌ Format: `/add_replace re1 black -> white`")
                    return

                await self.userbot.send_message('me', f"/replace add {text}")
                await event.reply("✅ Replacement rule added!")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/list_replace'))
        async def list_replace_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                await self.userbot.send_message('me', "/replace list")
                await event.reply("📋 Replacement list आपके userbot में check करें!")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/get_channels'))
        async def get_channels_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                await self.userbot.send_message('me', "/getchannel")
                await event.reply("📢 Channel list आपके userbot में check करें!")

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

        @self.bot.on(events.NewMessage(pattern='/userbot_status'))
        async def userbot_status_cmd(event):
            if not self.is_authorized(event.sender_id):
                await event.reply("❌ पहले /start भेजें")
                return

            try:
                userbot_me = await self.userbot.get_me()
                await event.reply(
                    f"🤖 **Userbot Status**\n\n"
                    f"✅ **Online**\n"
                    f"👤 Name: {userbot_me.first_name}\n"
                    f"📱 Username: @{userbot_me.username}\n"
                    f"🆔 ID: {userbot_me.id}\n"
                    f"📞 Phone: {userbot_me.phone}"
                )

            except Exception as e:
                await event.reply(f"❌ Error: {e}")

    def is_authorized(self, user_id):
        """Check authorization"""
        return user_id in self.authorized_users

    async def run(self):
        """Run the control bot"""
        if await self.start():
            print("🚀 Control Bot fully operational!")
            print("📱 Telegram पर अपने bot को /start भेजें")
            await self.bot.run_until_disconnected()
        else:
            print("❌ Failed to start control bot")

async def main():
    bot = FinalControlBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
