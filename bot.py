from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

import os
from dotenv import load_dotenv

load_dotenv()

# тут будем писать наш код :)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_GPT_TOKEN = os.getenv("OPENAI_TOKEN")

#print(f"Бот запущен\nТокен: {TELEGRAM_BOT_TOKEN}\nТокен для ChatGPT: {CHAT_GPT_TOKEN}")



async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(update, context, {
    "start": "главное меню бота",
    "profile": "генерация Tinder-профиля 😎",
    "opener": "сообщение для знакомства 🥰",
    "message": "переписка от вашего имени 😈",
    "date": "переписка со звездами 🔥",
    "gpt": "задать вопрос чату GPT 🧠"
    })

async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)

async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")

    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)

async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    else:
        await send_text(update, context, "*Привет*")
        await send_text(update, context, "_Как дела?_")
        await send_text(update, context, "Вы написали " + update.message.text)

        await send_photo(update, context, "avatar_main")
        await send_text_buttons(update, context, "Запустить процесс?", {
            "start": "Запустить",
            "stop": "Остановить"
        })    



async def hello_button(update, context):
    query = update.callback_query.data
    if query == "start":
        await send_text(update, context, "Процесс запущен")
    else:
        await send_text(update, context, "Процесс остановлен")

        
dialog= Dialog() # глобальная переменная для хранения состояния диалога
dialog.mode= None

chatgpt = ChatGptService (CHAT_GPT_TOKEN) # глобальная переменная для общения с ChatGPT

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
    
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(hello_button))
app.add_handler(CommandHandler("gpt", gpt))

app.run_polling()
