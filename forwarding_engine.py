""" Forwarding Engine Handles message forwarding logic and rules management """

import asyncio import logging import time from typing import Dict, List, Set from replacement_engine import ReplacementEngine

logger = logging.getLogger(name)

class ForwardingEngine: def init(self, client, config_manager): self.client = client self.config_manager = config_manager self.replacement_engine = ReplacementEngine(config_manager) self.forwarding_rules = {} self.message_cache = {}  # For tracking messages for editing self.active_tasks = set() self.running = False

async def start(self):
    """Start the forwarding engine"""
    self.running = True
    self.forwarding_rules = await self.config_manager.get_forwarding_rules()
    logger.info("Forwarding engine started")

async def stop(self):
    """Stop the forwarding engine"""
    self.running = False
    logger.info("Forwarding engine stopped")

async def restart(self):
    """Restart the forwarding engine"""
    await self.stop()
    await self.start()

async def add_forwarding_rule(self, label: str, source_ids: List[int], destination_ids: List[int]):
    """Add a new forwarding rule"""
    rule = {
        'label': label,
        'sources': source_ids,
        'destinations': destination_ids,
        'active': True,
        'delay': 0,
        'max_edit_time': 300,  # 5 minutes default
        'created_at': time.time()
    }

    self.forwarding_rules[label] = rule
    await self.config_manager.save_forwarding_rule(label, rule)
    logger.info(f"Added forwarding rule: {label}")

async def remove_forwarding_rule(self, label: str):
    """Remove a forwarding rule"""
    if label not in self.forwarding_rules:
        raise ValueError(f"Forwarding rule '{label}' not found")

    del self.forwarding_rules[label]
    await self.config_manager.remove_forwarding_rule(label)
    logger.info(f"Removed forwarding rule: {label}")

async def start_forwarding_rule(self, label: str):
    """Start a forwarding rule"""
    if label not in self.forwarding_rules:
        raise ValueError(f"Forwarding rule '{label}' not found")

    self.forwarding_rules[label]['active'] = True
    await self.config_manager.save_forwarding_rule(label, self.forwarding_rules[label])
    logger.info(f"Started forwarding rule: {label}")

async def stop_forwarding_rule(self, label: str):
    """Stop a forwarding rule"""
    if label not in self.forwarding_rules:
        raise ValueError(f"Forwarding rule '{label}' not found")

    self.forwarding_rules[label]['active'] = False
    await self.config_manager.save_forwarding_rule(label, self.forwarding_rules[label])
    logger.info(f"Stopped forwarding rule: {label}")

async def set_forwarding_delay(self, label: str, delay: int):
    """Set delay for a forwarding rule"""
    if label not in self.forwarding_rules:
        raise ValueError(f"Forwarding rule '{label}' not found")

    self.forwarding_rules[label]['delay'] = delay
    await self.config_manager.save_forwarding_rule(label, self.forwarding_rules[label])
    logger.info(f"Set delay for {label}: {delay}s")

async def set_max_edit_time(self, label: str, max_time: int):
    """Set max edit time for a forwarding rule"""
    if label not in self.forwarding_rules:
        raise ValueError(f"Forwarding rule '{label}' not found")

    self.forwarding_rules[label]['max_edit_time'] = max_time
    await self.config_manager.save_forwarding_rule(label, self.forwarding_rules[label])
    logger.info(f"Set max edit time for {label}: {max_time}s")

async def get_active_tasks(self):
    """Get list of active forwarding tasks"""
    return [
        {
            'label': rule['label'],
            'sources': rule['sources'],
            'destinations': rule['destinations'],
            'active': rule['active'],
            'delay': rule['delay'],
            'max_edit_time': rule['max_edit_time']
        }
        for rule in self.forwarding_rules.values()
    ]

async def process_message(self, event):
    """Process incoming message for forwarding"""
    if not self.running:
        logger.debug("Forwarding engine not running, skipping message")
        return

    source_id = event.chat_id
    logger.info(f"Processing message from {source_id}")

    # Find applicable forwarding rules
    applicable_rules = []
    for rule in self.forwarding_rules.values():
        logger.debug(f"Checking rule {rule['label']}: active={rule['active']}, sources={rule['sources']}")
        logger.debug(f"Source ID: {source_id}, Rule sources: {rule['sources']}")

        # Check if source matches (handle both formats)
        source_match = False
        for rule_source in rule['sources']:
            if source_id == rule_source:
                source_match = True
                break
            elif str(source_id).startswith('-100') and source_id == int(f"-100{abs(rule_source)}"):
                source_match = True
                break
            elif str(rule_source).startswith('-100') and rule_source == int(f"-100{abs(source_id)}"):
                source_match = True
                break

        if rule['active'] and source_match:
            applicable_rules.append(rule)
            logger.info(f"Found applicable rule: {rule['label']}")

    if not applicable_rules:
        logger.warning(f"No applicable rules found for source {source_id}")
        logger.info(f"Available rules: {[(rule['label'], rule['sources']) for rule in self.forwarding_rules.values()]}")
        return

    for rule in applicable_rules:
        try:
            logger.info(f"Processing rule {rule['label']}")
            await self._forward_message(event, rule)
        except Exception as e:
            logger.error(f"Error forwarding message with rule {rule['label']}: {e}")

async def _forward_message(self, event, rule):
    """Forward a message according to a rule"""
    try:
        if rule['delay'] > 0:
            await asyncio.sleep(rule['delay'])

        message = event.message
        original_text = message.text or message.caption or ""

        processed_text = await self.replacement_engine.process_text(original_text)

        message_key = f"{event.chat_id}_{message.id}"
        self.message_cache[message_key] = {
            'rule': rule,
            'forwarded_messages': [],
            'timestamp': time.time()
        }

        for dest_id in rule['destinations']:
            try:
                actual_dest_id = dest_id
                if not str(dest_id).startswith('-100') and dest_id < 0:
                    actual_dest_id = int(f"-100{abs(dest_id)}")

                logger.info(f"Forwarding to destination: {actual_dest_id}")

                if message.media:
                    if processed_text != original_text:
                        forwarded_msg = await self.client.send_message(
                            actual_dest_id,
                            processed_text,
                            file=message.media
                        )
                    else:
                        forwarded_msg = await self.client.forward_messages(
                            actual_dest_id,
                            message
                        )
                else:
                    forwarded_msg = await self.client.send_message(
                        actual_dest_id,
                        processed_text or original_text
                    )

                if isinstance(forwarded_msg, list):
                    forwarded_msg = forwarded_msg[0]

                self.message_cache[message_key]['forwarded_messages'].append({
                    'chat_id': dest_id,
                    'message_id': forwarded_msg.id
                })

                logger.info(f"Forwarded message from {event.chat_id} to {dest_id}")

            except Exception as e:
                logger.error(f"Error forwarding to {dest_id}: {e}")

    except Exception as e:
        logger.error(f"Error in _forward_message: {e}")

async def process_edited_message(self, event):
    """Process edited message for updating forwarded messages"""
    if not self.running:
        return

    message_key = f"{event.chat_id}_{event.message.id}"

    if message_key not in self.message_cache:
        return

    cache_entry = self.message_cache[message_key]
    rule = cache_entry['rule']

    if time.time() - cache_entry['timestamp'] > rule['max_edit_time']:
        del self.message_cache[message_key]
        return

    try:
        original_text = event.message.text or event.message.caption or ""
        processed_text = await self.replacement_engine.process_text(original_text)

        for forwarded_msg in cache_entry['forwarded_messages']:
            try:
                await self.client.edit_message(
                    forwarded_msg['chat_id'],
                    forwarded_msg['message_id'],
                    processed_text or original_text
                )
            except Exception as e:
                logger.error(f"Error editing forwarded message: {e}")

        logger.info(f"Updated forwarded messages for edited message {message_key}")

    except Exception as e:
        logger.error(f"Error processing edited message: {e}")

async def cleanup_old_cache_entries(self):
    """Clean up old cache entries"""
    current_time = time.time()
    keys_to_remove = []

    for key, cache_entry in self.message_cache.items():
        rule = cache_entry['rule']
        if current_time - cache_entry['timestamp'] > rule['max_edit_time']:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del self.message_cache[key]

