""" Utility functions for the Telegram userbot """

import re import logging from typing import List, Dict, Any

logger = logging.getLogger(name)

def parse_channel_ids(ids_str: str) -> List[int]: """Parse channel IDs from string format""" if not ids_str: return []

ids = []
parts = ids_str.split(',')

for part in parts:
    part = part.strip()
    if not part:
        continue
    
    try:
        ids.append(int(part))
    except ValueError:
        logger.warning(f"Invalid channel ID: {part}")
        continue

return ids

def format_channel_list(channels: List[Dict]) -> str: """Format channel list for display""" if not channels: return "No channels found"

lines = ["\ud83d\udce2 YOUR CHANNEL LIST\n"]

for i, channel in enumerate(channels, 1):
    username = f" (@{channel['username']})" if channel.get('username') else ""
    lines.append(f"{i}. {channel['title']}{username} -> (ID: {channel['id']})")

return "\n".join(lines)

def validate_regex(pattern: str) -> bool: """Validate regex pattern""" try: re.compile(pattern) return True except re.error: return False

def sanitize_text(text: str) -> str: """Sanitize text for safe processing""" if not text: return ""

text = text.replace('\x00', '')
max_length = 4096
if len(text) > max_length:
    text = text[:max_length]

return text

def extract_command_args(text: str) -> List[str]: """Extract command arguments from text""" args = [] current_arg = "" in_quotes = False

for char in text:
    if char == '"' and not in_quotes:
        in_quotes = True
    elif char == '"' and in_quotes:
        in_quotes = False
    elif char == ' ' and not in_quotes:
        if current_arg:
            args.append(current_arg)
            current_arg = ""
    else:
        current_arg += char

if current_arg:
    args.append(current_arg)

return args

def format_time_duration(seconds: int) -> str: """Format time duration in human readable format""" if seconds < 60: return f"{seconds}s" elif seconds < 3600: minutes = seconds // 60 remaining_seconds = seconds % 60 return f"{minutes}m {remaining_seconds}s" else: hours = seconds // 3600 remaining_minutes = (seconds % 3600) // 60 return f"{hours}h {remaining_minutes}m"

def is_valid_channel_id(channel_id: str) -> bool: """Check if channel ID is valid""" try: int(channel_id) return True except ValueError: return False

def clean_filename(filename: str) -> str: """Clean filename for safe file operations""" filename = re.sub(r'[<>:"/\|?*]', '_', filename) filename = filename.strip() if len(filename) > 255: filename = filename[:255] return filename

def parse_replacement_pattern(pattern: str) -> Dict[str, Any]: """Parse replacement pattern and extract metadata""" result = { 'type': 'simple', 'pattern': pattern, 'is_regex': False, 'is_full_text': False, 'is_all_in_one': False }

if pattern.startswith('(') and pattern.endswith(')'):
    result['type'] = 'regex'
    result['is_regex'] = True
    result['pattern'] = pattern[1:-1]
elif '[[FULL_TEXT]]' in pattern:
    result['type'] = 'full_text'
    result['is_full_text'] = True
elif '[[ALL_IN_ONE]]' in pattern:
    result['type'] = 'all_in_one'
    result['is_all_in_one'] = True

return result

