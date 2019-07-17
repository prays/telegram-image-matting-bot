import telebot
import requests
from os import environ

bot = telebot.TeleBot(environ['TELEGRAM_TOKEN'])

bot_text = '''
Sup, how are you doing?
Type 'Picture' to get pictures
Source code on https://glitch.com/~{}
'''.format(environ['PROJECT_NAME'])

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, bot_text)
  
# send unsplash picture
@bot.message_handler(regexp='(P|p)icture')
def send_pic(message):
  response = requests.get('https://source.unsplash.com/random')
  bot.send_photo(message.chat.id, response.content)

  
# echo handler
#@bot.message_handler(func=lambda m : True)
#def send_echo(message):
#	bot.send_message(message.chat.id, message.text)
  
  
  

bot.set_webhook("https://{}.glitch.me/{}".format(environ['PROJECT_NAME'], environ['TELEGRAM_TOKEN']))