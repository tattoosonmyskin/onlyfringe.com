"""
HexStrike AI MCP API Key Loader

Usage:
    from hexstrike_api_loader import load_api_keys
    api_keys = load_api_keys()
    openai_key = api_keys.get('OPENAI_API_KEY')
"""
import os

def load_api_keys(filename=".hexstrike_api_keys"):
    keys = {}
    if not os.path.exists(filename):
        return keys
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                keys[k.strip()] = v.strip()
    return keys
