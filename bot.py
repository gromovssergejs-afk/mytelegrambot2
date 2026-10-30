import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types

# Исправленный токен без опечатки
TOKEN = "9012470193:AAEqce7ISUgl9EzEQb0Wy9uBOMmtjsTjl88"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения участников группы
chat_users = {}

# 1. Команда /help (Справка)
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply(
        "Привет! Я бот для упоминания всех участников группы.\n\n"
        "📌 **Как пользоваться:**\n"
        "1. Участники общаются в чате — бот автоматически их запоминает.\n"
        "2. Напишите команду /all, чтобы призывно упомянуть всех!"
    )

# 2. Команда /all (Позвать всех)
@dp.message_handler(commands=['all'])
async def tag_all(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("Эта команда работает только в групповых чатах!")
        return
    
    chat_id = message.chat.id
    if chat_id not in chat_users or not chat_users[chat_id]:
        await message.reply("Пока никто ничего не написал в чате, некого тегать!")
        return

    users = chat_users[chat_id]
    tags = []
    
    # Экранируем специальные символы для Markdown, чтобы Telegram не выдавал ошибку
    for user_id, first_name in users.items():
        clean_name = first_name.replace('[', '').replace(']', '')
        tags.append(f"[{clean_name}](tg://user?id={user_id})")

    # Отправляем частями по 5 человек
    chunk_size = 5
    for i in range(0, len(tags), chunk_size):
        chunk = tags[i:i + chunk_size]
        text = "Внимание, сбор всех! 👇\n" + " ".join(chunk)
        await message.answer(text, parse_mode="Markdown")

# 3. Перехват сообщений (запоминаем активных участников)
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def track_users(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        user = message.from_user
        
        # Не запоминаем самих ботов
        if user.is_bot:
            return
            
        if chat_id not in chat_users:
            chat_users[chat_id] = {}
            
        chat_users[chat_id][user.id] = user.first_name

if __name__ == '__main__':
    # Безопасный запуск асинхронного цикла для системы Windows
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print("Бот успешно запущен и готов к работе!")
    executor.start_polling(dp, skip_updates=True, loop=loop)