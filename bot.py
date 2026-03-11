from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

import os
from dotenv import load_dotenv
load_dotenv()

# тут будем писать наш код :)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_GPT_TOKEN = os.getenv("OPENAI_TOKEN")

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


async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Следующее сообщение",
        "message_date": "Пригласить на свидание"
    })
    dialog.list.clear()

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    
    # Show a placeholder while waiting for the AI
    my_message = await send_text(update, context, "ChatGPT думает над вариантами ответ...")
    
    # Get the AI response
    answer = await chatgpt.send_question(prompt, user_chat_history)
    
    # Edit the original placeholder message with the actual answer
    await my_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.count = 0 # счетчик сообщений для отслеживания этапов диалога
    await send_text(update, context, "Для начала расскажите о себе: сколько Вам лет?")

async def profile_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Отлично!  Кем Вы работаете?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "Здорово!  Какие у Вас хобби?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Потрясающе!  Что Вам не нравится в людях?")
    elif dialog.count == 4:
        dialog.user["dislikes"] = text
        await send_text(update, context, "Спасибо за информацию! Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goal"] = text
        prompt = load_prompt("profile")
        user_info= dialog_user_info_to_str(dialog.user)
        answer= await chatgpt.send_question(prompt, user_info)
        await send_text(update, context, "Ваш сгенерированный профиль для Tinder:\n{}".format(answer))



async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)    
    else:
        await send_text(update, context, "*Привет*")
        await send_text(update, context, "_Как дела?_")
        await send_text(update, context, "Вы написали " + update.message.text)

        await send_photo(update, context, "avatar_main")



async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_grande": "Ариана Гранде",
        "date_robbie": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди"
    })

async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Девушка набирает текст...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update, context, "Отличный выбор! Пригласите девушку (парня) на свидание за 5 сообщений")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


dialog= Dialog() # глобальная переменная для хранения состояния диалога
dialog.mode= None
dialog.list = [] # сюда будем сохранять историю сообщений для передачи в ChatGPT
dialog.count = 0 # универсальный счетчик для отслеживания этапов диалога
dialog.user = {} # словарь для хранения информации о пользователе (для генерации профиля)



chatgpt = ChatGptService (CHAT_GPT_TOKEN) # глобальная переменная для общения с ChatGPT

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
    
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
#app.add_handler(CallbackQueryHandler(hello_button))
app.add_handler(CommandHandler("gpt", gpt))

app.add_handler(CommandHandler("message", message) )
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))

app.add_handler(CommandHandler("date", date))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))

app.add_handler(CommandHandler("profile", profile))


app.run_polling()
