"""
Replacement Engine
Handles text replacement with regex and special pattern support
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(name)

class ReplacementEngine:
def init(self, config_manager):
self.config_manager = config_manager
self.replacement_rules = {}

async def add_replacement_rule(self, label: str, original: str, replacement: str):  
    """Add a replacement rule"""  
    rule = {  
        'label': label,  
        'original': original,  
        'replacement': replacement,  
        'type': 'simple',  
        'active': True  
    }  
      
    # Detect rule type  
    if label.endswith('_regex'):  
        rule['type'] = 'regex'  
        # Extract regex pattern from parentheses  
        if original.startswith('(') and original.endswith(')'):  
            rule['pattern'] = original[1:-1]  
        else:  
            rule['pattern'] = original  
    elif '[[FULL_TEXT]]' in original:  
        rule['type'] = 'full_text'  
    elif '[[ALL_IN_ONE]]' in original:  
        rule['type'] = 'all_in_one'  
        rule['replacements'] = self._parse_all_in_one(replacement)  
      
    self.replacement_rules[label] = rule  
    await self.config_manager.save_replacement_rule(label, rule)  
    logger.info(f"Added replacement rule: {label}")  
  
async def remove_replacement_rule(self, label: str):  
    """Remove a replacement rule"""  
    if label not in self.replacement_rules:  
        raise ValueError(f"Replacement rule '{label}' not found")  
      
    del self.replacement_rules[label]  
    await self.config_manager.remove_replacement_rule(label)  
    logger.info(f"Removed replacement rule: {label}")  
  
async def get_replacement_rules(self):  
    """Get all replacement rules"""  
    return [  
        {  
            'label': rule['label'],  
            'type': rule['type'],  
            'original': rule.get('original', ''),  
            'pattern': rule.get('pattern', ''),  
            'replacement': rule['replacement'],  
            'active': rule['active']  
        }  
        for rule in self.replacement_rules.values()  
    ]  
  
async def clear_replacement_rules(self):  
    """Clear all replacement rules"""  
    self.replacement_rules.clear()  
    await self.config_manager.clear_replacement_rules()  
    logger.info("Cleared all replacement rules")  
  
def _parse_all_in_one(self, replacement_text: str) -> List[Dict]:  
    """Parse ALL_IN_ONE replacement format"""  
    replacements = []  
      
    # Split by comma and parse each replacement  
    parts = replacement_text.split(',')  
    for part in parts:  
        part = part.strip()  
        if '->' in part:  
            original, new = part.split('->', 1)  
            original = original.strip(' "')  
            new = new.strip(' "')  
              
            # Handle special formats  
            if original.startswith('regex:'):  
                replacements.append({  
                    'type': 'regex',  
                    'pattern': original[6:],  
                    'replacement': new  
                })  
            elif original.startswith('url:'):  
                replacements.append({  
                    'type': 'url',  
                    'tag': original[4:],  
                    'replacement': new  
                })  
            else:  
                replacements.append({  
                    'type': 'simple',  
                    'original': original,  
                    'replacement': new  
                })  
      
    return replacements  
  
async def process_text(self, text: str) -> str:  
    """Process text through all active replacement rules"""  
    if not text:  
        return text  
      
    processed_text = text  
      
    for rule in self.replacement_rules.values():  
        if not rule['active']:  
            continue  
          
        try:  
            processed_text = await self._apply_rule(processed_text, rule)  
        except Exception as e:  
            logger.error(f"Error applying replacement rule {rule['label']}: {e}")  
      
    return processed_text  
  
async def _apply_rule(self, text: str, rule: Dict) -> str:  
    """Apply a single replacement rule"""  
    rule_type = rule['type']  
      
    if rule_type == 'simple':  
        # Simple string replacement  
        return text.replace(rule['original'], rule['replacement'])  
      
    elif rule_type == 'regex':  
        # Regex replacement  
        pattern = rule['pattern']  
        replacement = rule['replacement']  
        return re.sub(pattern, replacement, text, flags=re.IGNORECASE)  
      
    elif rule_type == 'full_text':  
        # Replace entire text  
        return rule['replacement']  
      
    elif rule_type == 'all_in_one':  
        # Apply multiple replacements  
        result = text  
        for replacement in rule['replacements']:  
            result = await self._apply_single_replacement(result, replacement)  
        return result  
      
    return text  
  
async def _apply_single_replacement(self, text: str, replacement: Dict) -> str:  
    """Apply a single replacement from ALL_IN_ONE format"""  
    rep_type = replacement['type']  
      
    if rep_type == 'simple':  
        return text.replace(replacement['original'], replacement['replacement'])  
      
    elif rep_type == 'regex':  
        return re.sub(replacement['pattern'], replacement['replacement'], text, flags=re.IGNORECASE)  
      
    elif rep_type == 'url':  
        # Handle URL replacement (custom logic can be added here)  
        return text.replace(replacement['tag'], replacement['replacement'])  
      
    return text

