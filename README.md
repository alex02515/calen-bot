# Calorie Estimation Telegram Bot

A Python Telegram bot that estimates calories from food photos and text descriptions using OpenAI's API.

## Features

- 📸 **Photo Analysis**: Send a photo of food to get calorie estimates using OpenAI's vision API
- 📝 **Text Analysis**: Describe your food in text to get calorie estimates
- 🤖 **User-friendly**: Simple commands and clear responses
- ⚡ **Fast**: Quick processing and responses
- 🛡️ **Error Handling**: Graceful error handling with helpful messages

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

1. **Telegram Bot Token**:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the bot token

2. **OpenAI API Key**:
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create an account and get your API key

### 3. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Windows
set TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
set OPENAI_API_KEY=your_openai_api_key_here

# Linux/Mac
export TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
export OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Bot

```bash
python main.py
```

## Usage

1. Start a conversation with your bot on Telegram
2. Send `/start` to see the welcome message
3. Send `/help` for usage instructions
4. Send photos of food or text descriptions to get calorie estimates

### Examples

**Photo**: Send a clear photo of your meal

**Text descriptions**:
- "1 medium apple"
- "200g cooked rice"
- "1 slice of pizza"
- "2 eggs and toast"

## Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help and usage instructions

## Requirements

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Internet connection

## Notes

- Calorie estimates are approximate and should be used as a general guide
- The bot uses OpenAI's GPT-4o model for both vision and text analysis
- Processing time depends on image size and API response time
