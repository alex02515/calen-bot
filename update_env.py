#!/usr/bin/env python3
"""
Interactive script to update .env file with API keys
"""

import os

def update_env_file():
    print("🔧 Calorie Bot - API Keys Setup")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return
    
    print("📝 Please enter your API keys:")
    print()
    
    # Get Telegram Bot Token
    print("1. Telegram Bot Token:")
    print("   - Message @BotFather on Telegram")
    print("   - Send /newbot and follow instructions")
    print("   - Copy the bot token (looks like: 123456789:ABCdef...)")
    telegram_token = input("   Enter your Telegram Bot Token: ").strip()
    
    if not telegram_token:
        print("❌ Telegram Bot Token is required!")
        return
    
    # Get OpenAI API Key
    print("\n2. OpenAI API Key:")
    print("   - Go to https://platform.openai.com/")
    print("   - Sign up/login and get your API key")
    print("   - Copy the key (looks like: sk-...)")
    openai_key = input("   Enter your OpenAI API Key: ").strip()
    
    if not openai_key:
        print("❌ OpenAI API Key is required!")
        return
    
    # Update .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={telegram_token}

# OpenAI API Configuration
OPENAI_API_KEY={openai_key}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file updated successfully!")
        print("🚀 You can now run: python main.py")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    update_env_file()
