""" Command Handler Processes user commands for forwarding and replacement operations """

import re import logging from telethon.tl.types import Channel, Chat, User from utils import parse_channel_ids, format_channel_list

logger = logging.getLogger(name)

class CommandHandler: def init(self, client, forwarding_engine, replacement_engine, config_manager): self.client = client self.forwarding_engine = forwarding_engine self.replacement_engine = replacement_engine self.config_manager = config_manager

async def handle_command(self, event):
    """Process incoming commands"""
    text = event.message.text.strip()
    
    # Parse command
    parts = text.split()
    if not parts:
        return
    
    command = parts[0].lower()
    
    try:
        if command == '/forward':
            await self._handle_forward_command(event, parts[1:])
        elif command == '/replace':
            await self._handle_replace_command(event, parts[1:])
        elif command == '/getchannel':
            await self._handle_getchannel_command(event)
        else:
            await event.reply("\u274c Unknown command. Use /forward, /replace, or /getchannel")
    
    except Exception as e:
        logger.error(f"Command error: {e}")
        await event.reply(f"\u274c Error: {e}")

# Forward Commands
async def _handle_forward_command(self, event, args):
    """Handle forward commands"""
    if not args:
        await event.reply(
            "\ud83d\udccb Forward Commands:\n"
            "/forward add [LABEL] [SOURCE_ID] -> [DESTINATION_ID]\n"
            "/forward remove [LABEL]\n"
            "/forward start [LABEL]\n"
            "/forward stop [LABEL]\n"
            "/forward delay [LABEL] [SECONDS]\n"
            "/forward max_time_edit [LABEL] [SECONDS]\n"
            "/forward restart\n"
            "/forward task"
        )
        return

    subcommand = args[0].lower()
    if subcommand == 'add':
        await self._handle_forward_add(event, args[1:])
    elif subcommand == 'remove':
        await self._handle_forward_remove(event, args[1:])
    elif subcommand == 'start':
        await self._handle_forward_start(event, args[1:])
    elif subcommand == 'stop':
        await self._handle_forward_stop(event, args[1:])
    elif subcommand == 'delay':
        await self._handle_forward_delay(event, args[1:])
    elif subcommand == 'max_time_edit':
        await self._handle_forward_max_time_edit(event, args[1:])
    elif subcommand == 'restart':
        await self._handle_forward_restart(event)
    elif subcommand == 'task':
        await self._handle_forward_task(event)
    else:
        await event.reply("\u274c Unknown forward subcommand")

async def _handle_forward_add(self, event, args):
    if len(args) < 3 or '->' not in ' '.join(args):
        await event.reply("\u274c Usage: /forward add [LABEL] [SOURCE_ID] -> [DESTINATION_ID]")
        return

    text = ' '.join(args)
    parts = text.split('->')
    left_part = parts[0].strip().split()
    right_part = parts[1].strip()

    label = left_part[0]
    source_ids_str = ' '.join(left_part[1:])
    try:
        source_ids = parse_channel_ids(source_ids_str)
        destination_ids = parse_channel_ids(right_part)
        await self.forwarding_engine.add_forwarding_rule(label, source_ids, destination_ids)
        await event.reply(f"\u2705 Added forwarding rule '{label}'\n"
                          f"\ud83d\udce4 Sources: {', '.join(map(str, source_ids))}\n"
                          f"\ud83d\udce5 Destinations: {', '.join(map(str, destination_ids))}")
    except Exception as e:
        await event.reply(f"\u274c Error adding forwarding rule: {e}")

async def _handle_forward_remove(self, event, args):
    if not args:
        await event.reply("\u274c Usage: /forward remove [LABEL]")
        return
    label = args[0]
    try:
        await self.forwarding_engine.remove_forwarding_rule(label)
        await event.reply(f"\u2705 Removed forwarding rule '{label}'")
    except Exception as e:
        await event.reply(f"\u274c Error removing forwarding rule: {e}")

async def _handle_forward_start(self, event, args):
    if not args:
        await event.reply("\u274c Usage: /forward start [LABEL]")
        return
    label = args[0]
    try:
        await self.forwarding_engine.start_forwarding_rule(label)
        await event.reply(f"\u25b6\ufe0f Started forwarding rule '{label}'")
    except Exception as e:
        await event.reply(f"\u274c Error starting forwarding rule: {e}")

async def _handle_forward_stop(self, event, args):
    if not args:
        await event.reply("\u274c Usage: /forward stop [LABEL]")
        return
    label = args[0]
    try:
        await self.forwarding_engine.stop_forwarding_rule(label)
        await event.reply(f"\u23f9\ufe0f Stopped forwarding rule '{label}'")
    except Exception as e:
        await event.reply(f"\u274c Error stopping forwarding rule: {e}")

async def _handle_forward_delay(self, event, args):
    if len(args) < 2:
        await event.reply("\u274c Usage: /forward delay [LABEL] [SECONDS]")
        return
    label = args[0]
    try:
        delay = int(args[1])
        await self.forwarding_engine.set_forwarding_delay(label, delay)
        await event.reply(f"\u23f1\ufe0f Set delay for '{label}' to {delay} seconds")
    except Exception as e:
        await event.reply(f"\u274c Error setting delay: {e}")

async def _handle_forward_max_time_edit(self, event, args):
    if len(args) < 2:
        await event.reply("\u274c Usage: /forward max_time_edit [LABEL] [SECONDS]")
        return
    label = args[0]
    try:
        max_time = int(args[1])
        await self.forwarding_engine.set_max_edit_time(label, max_time)
        await event.reply(f"\u23f0 Set max edit time for '{label}' to {max_time} seconds")
    except Exception as e:
        await event.reply(f"\u274c Error setting max edit time: {e}")

async def _handle_forward_restart(self, event):
    try:
        await self.forwarding_engine.restart()
        await event.reply("\ud83d\udd04 Forwarding engine restarted")
    except Exception as e:
        await event.reply(f"\u274c Error restarting: {e}")

async def _handle_forward_task(self, event):
    try:
        tasks = await self.forwarding_engine.get_active_tasks()
        if not tasks:
            await event.reply("\ud83d\udccb No active forwarding tasks")
            return
        message = "\ud83d\udccb Active Forwarding Tasks:\n\n"
        for task in tasks:
            status = "\u25b6\ufe0f" if task['active'] else "\u23f8\ufe0f"
            message += f"{status} {task['label']}\n"
            message += f"   \ud83d\udce4 Sources: {', '.join(map(str, task['sources']))}\n"
            message += f"   \ud83d\udce5 Destinations: {', '.join(map(str, task['destinations']))}\n"
            message += f"   \u23f1\ufe0f Delay: {task['delay']}s\n"
            message += f"   \u23f0 Max Edit: {task['max_edit_time']}s\n\n"
        await event.reply(message)
    except Exception as e:
        await event.reply(f"\u274c Error getting tasks: {e}")

# Replace Commands - OMITTED for BREVITY

# GetChannel Command
async def _handle_getchannel_command(self, event):
    try:
        channels = []
        async for dialog in self.client.iter_dialogs():
            entity = dialog.entity
            if getattr(entity, 'broadcast', False) or getattr(entity, 'megagroup', False):
                channels.append({
                    'title': dialog.title,
                    'id': entity.id,
                    'username': getattr(entity, 'username', None)
                })
        if not channels:
            await event.reply("\ud83d\udce2 No channels found")
            return
        message = "Auto Forward Messages:\n\ud83d\udce2 YOUR CHANNEL LIST\n\n"
        for i, ch in enumerate(channels, 1):
            uname = f" (@{ch['username']})" if ch['username'] else ""
            message += f"{i}. {ch['title']}{uname} -> (ID: {ch['id']})\n"
        await event.reply(message)
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        await event.reply(f"\u274c Error getting channels: {e}")

