import telebot
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import random

load_dotenv()

TELEGRAB_KEY = '8313937350:AAHgGhFhrMpyMkPUjT24u1nj3jG3q553mgU'  
bot = telebot.TeleBot(TELEGRAB_KEY)


# --- Команды ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот который поможет не только бояться но и помогать природе.\nКоманды:\n/donat - поддержать экологические проекты через донаты.\n/report - сообщить о несанкционированных свалках.\n/advice - получить советы по экологии.\n/news - последние новости об экологии.")

@bot.message_handler(commands=['donat'])
def send_donat(message):
    bot.reply_to(message, "Вы можете поддержать природу скинув донат на эту карту ******. Спасибо за вашу помощь!")

@bot.message_handler(commands=['report'])
def send_report(message):
    bot.reply_to(message, "Чтобы сообщить о несанкционированной свалке, отправьте фото и описание места на этот номер: +7-999-999-99-99.")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    # сохраняем в отдельную папку reports/
    os.makedirs("reports", exist_ok=True)

    path = f"reports/{file_id}.jpg"
    with open(path, "wb") as f:
        f.write(downloaded)

    bot.reply_to(message, f"Фото получено и сохранено!\nФайл: {path}")

@bot.message_handler(commands=['advice'])
def send_advice(message):
    with open("советы.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()  # список, где каждая строка файла — один элемент
    lines = [line.strip() for line in lines]  # убираем переносы
    sovets = random.choice(lines)
    bot.reply_to(message, sovets)

# --- Поиск новостей через RSS ---
def get_eco_news():
    url = "https://tengrinews.kz/tag/экология/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")

    items = soup.find_all("div", class_='content_main_item')[:5]  # первые 5 новостей
    news = []

    for item in items:
        title_tag = item.find('span', class_='content_main_item_title')
        link_tag = item.find('a', href=True)
        if title_tag and link_tag:
            news.append(f"{title_tag.text.strip()}\nhttps://tengrinews.kz{link_tag['href']}")
    return news


@bot.message_handler(commands=['news'])
def send_news(message):
    try:
        news_list = get_eco_news()
        if news_list:
            bot.reply_to(message, "\n\n".join(news_list))
        else:
            bot.reply_to(message, "Не удалось найти новости. Попробуйте позже.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при получении новостей: {e}")

# --- Запуск бота ---
bot.polling()
