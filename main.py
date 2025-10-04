#!/usr/bin/env python3
"""
Telegram Bot для определения калорий в еде

Этот бот может определить калории из:
1. Фотографий еды используя OpenAI Vision API
2. Текстовых описаний используя OpenAI Text API

Необходимые переменные окружения:
- TELEGRAM_BOT_TOKEN: Токен вашего Telegram бота
- OPENAI_API_KEY: Ваш OpenAI API ключ
"""

import os
import logging
import asyncio
from io import BytesIO
from typing import Optional
import hashlib

import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from PIL import Image
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация OpenAI клиента
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Конфигурация бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# ===== НАСТРОЙКИ ИНТЕРФЕЙСА =====
# Здесь можно изменить тексты и кнопки бота

# Тексты кнопок (можно изменить здесь)
BUTTON_START = "🏠 Старт"
BUTTON_ANALYZE_PHOTO = "📸 Анализ блюда"
BUTTON_SEARCH_CALORIES = "🔍 Поиск калорий"
BUTTON_HELP = "❓ Помощь"

# Создание клавиатуры
def get_main_keyboard():
    """Создает основную клавиатуру с кнопками"""
    keyboard = [
        [BUTTON_ANALYZE_PHOTO, BUTTON_SEARCH_CALORIES],
        [BUTTON_HELP, BUTTON_START]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

class CalorieBot:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=openai.api_key)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        welcome_message = """
🍎 Добро пожаловать в бот подсчета калорий! 🍎

Я помогу вам определить калории в еде:
📸 Фото еды - просто отправьте мне фотографию
📝 Описание - расскажите что вы ели (например, "2 яблока и 200г риса")

Используйте кнопки внизу для навигации!
        """
        await update.message.reply_text(
            welcome_message, 
            reply_markup=get_main_keyboard()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        help_message = """
❓ Помощь - Бот подсчета калорий

Как пользоваться:
📸 "Анализ блюда" → отправьте фото еды
🔍 "Поиск калорий" → опишите еду текстом

Примеры описаний:
• "2 яблока"
• "200г вареного риса" 
• "1 кусок пиццы"
• "2 яйца и хлеб"

💡 Калории указаны приблизительно, используйте как ориентир.
        """
        await update.message.reply_text(
            help_message,
            reply_markup=get_main_keyboard()
        )
    
    async def handle_button_press(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик нажатий кнопок и текстовых сообщений"""
        text = update.message.text
        
        # Проверяем, нажата ли кнопка
        if text == BUTTON_START:
            await self.start_command(update, context)
        elif text == BUTTON_ANALYZE_PHOTO:
            await self.handle_analyze_photo_button(update, context)
        elif text == BUTTON_SEARCH_CALORIES:
            await self.handle_search_calories_button(update, context)
        elif text == BUTTON_HELP:
            await self.help_command(update, context)
        else:
            # Если это не кнопка, то это текстовое описание еды
            await self.handle_text(update, context)
    
    async def handle_analyze_photo_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик кнопки 'Анализ блюда'"""
        message = """
📸 Анализ блюда

Отправьте мне фотографию еды, и я определю:
• Что изображено на фото
• Приблизительный размер порции  
• Количество калорий

Просто отправьте фото! 📷
        """
        await update.message.reply_text(message)
    
    async def handle_search_calories_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик кнопки 'Поиск калорий'"""
        message = """
🔍 Поиск калорий

Опишите что вы ели, и я подсчитаю калории.

Примеры:
• "2 яблока"
• "200г вареного риса"
• "1 кусок пиццы"
• "2 яйца и хлеб"

Напишите что вы ели! ✍️
        """
        await update.message.reply_text(message)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик фотографий с оптимизированной скоростью"""
        try:
            # Немедленная обратная связь
            processing_msg = await update.message.reply_text("🔍 Анализирую ваше фото...", reply_markup=get_main_keyboard())
            
            # Получаем фото в наилучшем качестве
            photo = update.message.photo[-1]
            
            # Скачиваем фото
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()
            
            # Проверяем размер фото
            if len(photo_bytes) < 1000:
                await update.message.reply_text(
                    "⚠️ Фото слишком маленькое для качественного анализа. Попробуйте отправить фото в лучшем качестве.",
                    reply_markup=get_main_keyboard()
                )
                return
            
            # Обрабатываем фото
            result = await self.analyze_food_photo_with_progress(photo_bytes, processing_msg)
            
            # Отправляем результат
            await update.message.reply_text(result, reply_markup=get_main_keyboard())
            
        except Exception as e:
            logger.error(f"Error processing photo: {e}")
            await update.message.reply_text(
                "❌ Извините, не смог обработать фото. Попробуйте отправить более четкое изображение еды.",
                reply_markup=get_main_keyboard()
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений с оптимизацией"""
        try:
            # Немедленная обратная связь
            processing_msg = await update.message.reply_text("🔍 Анализирую описание еды...", reply_markup=get_main_keyboard())
            
            # Обрабатываем текст
            result = await self.analyze_food_text_with_progress(update.message.text, processing_msg)
            
            # Отправляем результат
            await update.message.reply_text(result, reply_markup=get_main_keyboard())
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            await update.message.reply_text(
                "❌ Извините, не смог обработать сообщение. Попробуйте описать еду более четко.",
                reply_markup=get_main_keyboard()
            )
    
    async def analyze_food_photo_with_progress(self, photo_bytes: bytes, processing_msg) -> str:
        """Быстрый и простой анализ фото"""
        try:
            # Проверяем размер фото
            if len(photo_bytes) < 1000:
                return "❌ Фото слишком маленькое. Попробуйте другое."
            
            # Конвертируем байты в base64
            import base64
            from PIL import Image
            import io
            
            # Проверяем и конвертируем изображение в JPEG
            try:
                # Открываем изображение
                image = Image.open(io.BytesIO(photo_bytes))
                
                # Конвертируем в RGB если нужно
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                # Сжимаем изображение для экономии
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                
                # Сохраняем в JPEG
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='JPEG', quality=85, optimize=True)
                img_buffer.seek(0)
                
                # Конвертируем в base64
                base64_image = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
            except Exception as img_error:
                logger.error(f"Error processing image: {img_error}")
                # Fallback - используем оригинальные байты
                base64_image = base64.b64encode(photo_bytes).decode('utf-8')
            
            # Один быстрый анализ
            result = await self._single_food_analysis(base64_image)
            
            return f"📸 {result}"
            
        except Exception as e:
            logger.error(f"Error in photo analysis: {e}")
            return "❌ Ошибка при анализе. Попробуйте еще раз."

    
    
    
    
    async def _single_food_analysis(self, base64_image: str) -> str:
        """Проверяет наличие еды и анализирует калории в одном запросе"""
        try:
            # Проверяем размер изображения
            if len(base64_image) < 1000:
                return "❌ Фото слишком маленькое. Попробуйте другое."
            
            # Проверяем API ключ
            if not self.openai_client.api_key:
                logger.error("OpenAI API key is not set")
                return "❌ Ошибка конфигурации. Обратитесь к администратору."
            
            # Один запрос: проверяем еду и анализируем калории
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Есть ли еда на фото? Еда включает: готовые блюда, сырые продукты, орехи, семечки, сухофрукты, крупы, фрукты, овощи. Если есть - оцени размер порции в граммах и рассчитай калории для этой порции. НЕ давай калории на 100г. ВАЖНО: 1 сосиска = ~150 ккал, 2 сосиски = ~300 ккал. Если нет еды - ответь 'НЕТ_ЕДЫ'. Формат: 'Продукт (~XXг) — ~XXX ккал'"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "low"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=80,
                    temperature=0.1
                ),
                timeout=15.0
            )
            
            result = response.choices[0].message.content.strip()
            
            # Проверяем, что получили разумный ответ
            if not result or len(result) < 5:
                return "❌ Не смог распознать изображение. Попробуйте другое фото."
            
            # Проверяем, есть ли еда на фото
            if "НЕТ_ЕДЫ" in result.upper() or "НЕТ ЕДЫ" in result.upper():
                return "❌ На фото не удалось найти еду."
            
            return result
            
        except asyncio.TimeoutError:
            return "⏰ Анализ занял слишком много времени. Попробуйте другое фото."
        except Exception as e:
            logger.error(f"Error in food analysis: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            return "❌ Ошибка при анализе. Попробуйте еще раз."
    
    
    
    async def _single_text_analysis(self, text: str) -> str:
        """Проверяет, описывает ли текст еду, и анализирует калории"""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user", 
                            "content": f"Это еда: '{text}'? Еда включает: готовые блюда, сырые продукты, орехи, семечки, сухофрукты, крупы, фрукты, овощи. Если да - оцени размер порции в граммах и рассчитай калории для этой порции. НЕ давай калории на 100г. ВАЖНО: 1 сосиска = ~150 ккал, 2 сосиски = ~300 ккал. Если нет еды - ответь 'НЕТ_ЕДЫ'. Формат: 'Продукт (~XXг) — ~XXX ккал'"
                        }
                    ],
                    max_tokens=60,
                    temperature=0.1
                ),
                timeout=6.0
            )
            
            result = response.choices[0].message.content.strip()
            
            # Проверяем, описывает ли текст еду
            if "НЕТ_ЕДЫ" in result.upper() or "НЕТ ЕДЫ" in result.upper():
                return "❌ В описании не удалось найти еду."
            
            return result
            
        except asyncio.TimeoutError:
            return "⏰ Анализ занял слишком много времени. Попробуйте другое описание."
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return "❌ Ошибка при анализе. Попробуйте еще раз."
    
    async def analyze_food_text_with_progress(self, text: str, processing_msg) -> str:
        """Быстрый анализ текста"""
        try:
            # Один быстрый анализ
            result = await self._single_text_analysis(text)
            
            return f"📝 {result}"
            
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return "❌ Не смог проанализировать описание. Попробуйте еще раз."
    
    
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик ошибок - логирует ошибку и уведомляет пользователя"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Извините, что-то пошло не так. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )

def main():
    """Запуск бота"""
    # Создаем экземпляр бота
    bot = CalorieBot()
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_button_press))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(bot.error_handler)
    
    # Запускаем бота
    logger.info("Starting Calorie Estimation Bot...")
    print("🤖 Бот подсчета калорий запущен!")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n👋 Бот остановлен. До свидания!")

if __name__ == '__main__':
    main()
