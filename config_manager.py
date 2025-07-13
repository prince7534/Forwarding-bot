"""
Configuration Manager
Handles persistent storage of forwarding rules and settings
"""

import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_file='userbot_config.json'):
        self.config_file = config_file
        self.config = {
            'forwarding_rules': {},
            'replacement_rules': {},
            'settings': {}
        }
    
    async def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info("Configuration loaded successfully")
            else:
                logger.info("No configuration file found, using defaults")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Use default config on error
            self.config = {
                'forwarding_rules': {},
                'replacement_rules': {},
                'settings': {}
            }
    
    async def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    async def get_forwarding_rules(self) -> Dict:
        """Get all forwarding rules"""
        return self.config.get('forwarding_rules', {})
    
    async def save_forwarding_rule(self, label: str, rule: Dict):
        """Save a forwarding rule"""
        if 'forwarding_rules' not in self.config:
            self.config['forwarding_rules'] = {}
        
        self.config['forwarding_rules'][label] = rule
        await self.save_config()
    
    async def remove_forwarding_rule(self, label: str):
        """Remove a forwarding rule"""
        if 'forwarding_rules' in self.config and label in self.config['forwarding_rules']:
            del self.config['forwarding_rules'][label]
            await self.save_config()
    
    async def get_replacement_rules(self) -> Dict:
        """Get all replacement rules"""
        return self.config.get('replacement_rules', {})
    
    async def save_replacement_rule(self, label: str, rule: Dict):
        """Save a replacement rule"""
        if 'replacement_rules' not in self.config:
            self.config['replacement_rules'] = {}
        
        self.config['replacement_rules'][label] = rule
        await self.save_config()
    
    async def remove_replacement_rule(self, label: str):
        """Remove a replacement rule"""
        if 'replacement_rules' in self.config and label in self.config['replacement_rules']:
            del self.config['replacement_rules'][label]
            await self.save_config()
    
    async def clear_replacement_rules(self):
        """Clear all replacement rules"""
        self.config['replacement_rules'] = {}
        await self.save_config()
    
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.config.get('settings', {}).get(key, default)
    
    async def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        
        self.config['settings'][key] = value
        await self.save_config()
