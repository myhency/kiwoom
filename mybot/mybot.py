import json
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler


class MyBot:
    def __init__(self):
        with open('./config/app.config.json', 'r') as f:
            self.config = json.load(f)

        self.updater = Updater(token=self.config['TELEGRAM']['TOKEN'], use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.bot = telegram.Bot(self.config['TELEGRAM']['TOKEN'])

    def send_message_to_my_bot(self, message):
        self.bot.sendMessage(chat_id=self.config['TELEGRAM']['BOT_ID'], text=message)

    def send_message_to_my_channel(self, message):
        # channel 생성에 도움된 영상 https://www.youtube.com/watch?v=zGhkAIe1BIg
        self.bot.sendMessage(chat_id=self.config['TELEGRAM']['CHANNEL_ID'], text=message)
