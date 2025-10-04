#!/usr/bin/env python3
"""
Setup script to help configure environment variables for the Calorie Bot
"""

import os
import sys

def setup_environment():
    """Interactive setup for environment variables"""
    print("🤖 Calorie Estimation Bot Setup")
    print("=" * 40)
    
    # Check if variables are already set
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if telegram_token and openai_key:
        print("✅ Environment variables are already set!")
        print(f"Telegram Token: {telegram_token[:10]}...")
        print(f"OpenAI Key: {openai_key[:10]}...")
        return True
    
    print("\n📝 You need to set up your API keys:")
    print("\n1. Get your Telegram Bot Token:")
    print("   - Message @BotFather on Telegram")
    print("   - Create a new bot with /newbot")
    print("   - Copy the bot token")
    
    print("\n2. Get your OpenAI API Key:")
    print("   - Go to https://platform.openai.com/")
    print("   - Create an account and get your API key")
    
    print("\n3. Set the environment variables:")
    print("   For Windows (Command Prompt):")
    print("   set TELEGRAM_BOT_TOKEN=your_token_here")
    print("   set OPENAI_API_KEY=your_key_here")
    
    print("\n   For Windows (PowerShell):")
    print("   $env:TELEGRAM_BOT_TOKEN='your_token_here'")
    print("   $env:OPENAI_API_KEY='your_key_here'")
    
    print("\n   For Linux/Mac:")
    print("   export TELEGRAM_BOT_TOKEN=your_token_here")
    print("   export OPENAI_API_KEY=your_key_here")
    
    print("\n4. Then run: python main.py")
    
    return False

if __name__ == "__main__":
    setup_environment()
