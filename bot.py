# import required libraries
import telebot
import datetime
import requests
import urllib.request
import subprocess
import os

import numpy as np
import cv2

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms

from os import environ

from src.models.modnet import MODNet

# setup bot with Telegram token from .env
#print(environ)
bot = telebot.TeleBot(environ['TELEGRAM_TOKEN'])

bot_text = '''
Bip-bop human,

I classify images using neural networks 🚀

Send me pictures, and I will matting them for you 🤟

Created with ❤️ by Alain Perkaz. @wh_image_classificator_bot
Source code on https://glitch.com/~telegram-image-classfication-bot

Modify by Pray Somaldo
'''



# store files in /tmp so storage does not get complete  
result_storage_path = 'tmp'  

@bot.message_handler(commands=['start'])
def send_welcome(message):
 bot.send_message(message.chat.id, bot_text)

@bot.message_handler(content_types=['photo'])
def handle(message):
  
  log_request(message)
  
  image_name = save_image_from_message(message)
  
  # object recognition
  object_recognition_image(image_name)
  bot.send_photo(message.chat.id, open('.tmp/{}'.format(image_name),'rb'), 'Here is your Matting photo! 🚀')
  
  # image classification
  #classification_list_result = classify_image(image_name)
  
  # send classification results
  #output = 'The image classifies as:\n'
  #for result in classification_list_result:
  #  output += result
  #output += '\n🚀 Give more pics! 🚀'
  output = 'Try another photo' 

  bot.reply_to(message, output)
  
  cleanup_remove_image(image_name);  
  
  
  
  
# ----------- Helper functions ---------------

def log_request(message):
  file = open('.data/logs.txt', 'a') #append to file
  file.write("{0} - {1} {2} [{3}]\n".format(datetime.datetime.now(), message.from_user.first_name, message.from_user.last_name, message.from_user.id)) 
  print("{0} - {1} {2} [{3}]".format(datetime.datetime.now(), message.from_user.first_name, message.from_user.last_name, message.from_user.id))
  file.close() 
  

def get_image_id_from_message(message):
  # there are multiple array of images, check the biggest
  return message.photo[len(message.photo)-1].file_id


def save_image_from_message(message):
  cid = message.chat.id
  
  image_id = get_image_id_from_message(message)
  
  bot.send_message(cid, '🔥 Matting image, be patient ! 🔥')
  
  # prepare image for downlading
  file_path = bot.get_file(image_id).file_path

  # generate image download url
  image_url = "https://api.telegram.org/file/bot{0}/{1}".format(environ['TELEGRAM_TOKEN'], file_path)
  print(image_url)
  
  # create folder to store pic temporary, if it doesnt exist
  if not os.path.exists(result_storage_path):
    os.makedirs(result_storage_path)
  
  # retrieve and save image
  image_name = "{0}.jpg".format(image_id)
  urllib.request.urlretrieve(image_url, "{0}/{1}".format(result_storage_path,image_name))
  
  return image_name

'''
def classify_image(image_name):
  # classify image -> https://pjreddie.com/darknet/imagenet/
  os.system('cd .data/darknet && ./darknet classifier predict cfg/imagenet1k.data cfg/darknet19.cfg darknet19.weights ../../{0}/{1} > ../../{0}/results.txt'.format(result_storage_path, image_name)) 
  
  # retrieve classification results
  results_file = open("{0}/results.txt".format(result_storage_path),"r") 
  results = results_file.readlines()
  results_file.close()
  
  return results
''' 

def object_recognition_image(image_name):
  # object recognition -> https://pjreddie.com/darknet/yolo/
  #os.system('cd .data/darknet && ./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights ../../{0}/{1}'.format(result_storage_path, image_name)) 
  os.system('python3 inference.py --input-path {0}/{1} --output-path .tmp/{1} --ckpt-path pretrained/modnet_photographic_portrait_matting.ckpt'.format(result_storage_path, image_name))

  
  
def cleanup_remove_image(image_name):
  os.remove('{0}/{1}'.format(result_storage_path, image_name))

  
  
  
  
# configure the webhook for the bot, with the url of the Glitch project
bot.set_webhook("https://{}.glitch.me/{}".format(environ['PROJECT_NAME'], environ['TELEGRAM_TOKEN']))