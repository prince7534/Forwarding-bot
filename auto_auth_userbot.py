#!/usr/bin/env python3  
"""
Auto Authentication Userbot  
Automatically handles phone and code input  
"""

import asyncio  
import os  
import sys  
import logging  
from telethon import TelegramClient  
from bot_manager import TelegramUserbot

# Configure logging  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
    handlers=[  
        logging.FileHandler('userbot.log'),  
        logging.StreamHandler(sys.stdout)  
    ]  
)

logger = logging.getLogger(__name__)  # "__name__" corrected from "name"

async def main():  
    """Main application entry point with auto authentication"""  
    try:  
        print("🤖 Telegram Userbot Starting...")  
        print("=" * 50)  

        # Credentials    
        api_id = 23752062    
        api_hash = "d263514cba2e798b082917ffb62393cc"    
        phone = "+917534016452"    
        code = "10643"    

        # Create client    
        client = TelegramClient('session', api_id, api_hash)    

        # Start with phone and code    
        await client.start(phone=phone, code_callback=lambda: code)    

        # Get user info    
        me = await client.get_me()    
        print(f"✅ Logged in as: {me.first_name} (@{me.username})")    

        # Create userbot instance    
        userbot = TelegramUserbot(api_id, api_hash)    
        userbot.client = client  # Use authenticated client    

        # Initialize all components with the correct client    
        userbot.config_manager.client = client    
        userbot.forwarding_engine.client = client    
        userbot.replacement_engine.client = client    
        userbot.command_handler.client = client    

        # Load configuration    
        await userbot.config_manager.load_config()    

        # Start forwarding engine    
        await userbot.forwarding_engine.start()    

        # Register message handlers    
        userbot._register_handlers()    
        print("✅ Event handlers registered")    

        # Test forwarding engine    
        print(f"✅ Forwarding engine running: {userbot.forwarding_engine.running}")    
        print(f"✅ Active rules: {len(userbot.forwarding_engine.forwarding_rules)}")    

        for label, rule in userbot.forwarding_engine.forwarding_rules.items():    
            print(f"  - {label}: {rule['sources']} -> {rule['destinations']} (active: {rule['active']})")    

        print("✅ Userbot started successfully!")    
        print("📱 Send commands to control the bot:")    
        print("   /forward add [LABEL] [SOURCE_ID] -> [DESTINATION_ID]")    
        print("   /replace add [LABEL] [ORIGINAL] -> [REPLACEMENT]")    
        print("   /getchannel - List all channels")    
        print("   /forward task - Show active forwarding tasks")    
        print("\n🔄 Bot is running... Press Ctrl+C to stop")    

        # Keep the bot running    
        await client.run_until_disconnected()    

    except KeyboardInterrupt:    
        print("\n🛑 Userbot stopped by user")    
    except Exception as e:    
        logger.error(f"Fatal error: {e}")    
        print(f"❌ Fatal error: {e}")    
        sys.exit(1)  

if __name__ == "__main__":  
    asyncio.run(main())
