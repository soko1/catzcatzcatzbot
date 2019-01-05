#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a universal telegram-bot for displaying Instagram pictures by tag.
Originally written as a bot to show cats :)
By the way, subscribe: @catzcatzcatzbot

Get the code: https://github.com/soko1/catzcatzcatzbot

# Contacts

@gnupg (telegram)
nullbsd@gmail.com (email)

# Donate

Do you want feed my cat?

Bitcoin: 1NYYFoJiRPnkmFbcv5kYLqwsweix1cVmBT

(Webmoney)

WMZ: Z156396869707
WMR: R409106892241
WME: E320058433666
"""


import logging
import os
import asyncio
import re
import argparse
import configparser
import telepot
import telepot.aio
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import instagram_explore as ie

PARSER = argparse.ArgumentParser(description='Help')
PARSER.add_argument('-c', help='path to config', metavar='config', type=str)
ARGS = PARSER.parse_args()

if ARGS.c is None:
    PARSER.print_help()
    exit(0)


# multistart protection
CHECKPROC = os.popen("ps aux | grep %s.*%s" % (__file__, ARGS.c)).read()
if CHECKPROC.count("python") > 1:
    print("The bot is already running")
    os._exit(1)

CONFIG = configparser.ConfigParser()
CONFIG.read(ARGS.c)

BOT_API = CONFIG['SYSTEM']['BOT_API']
TAG = CONFIG['SYSTEM']['TAG']

# messages
DONATE = CONFIG['MESSAGES']['DONATE']
DONATE_PICTURE = CONFIG['MESSAGES']['DONATE_PICTURE']
CONTACTS = CONFIG['MESSAGES']['CONTACTS']
HELP = CONFIG['MESSAGES']['HELP']
DESCRIPTION_PICTURE = CONFIG['MESSAGES']['DESCRIPTION_PICTURE']

# buttons
PICTURE_BUTTON = CONFIG['MESSAGES']['PICTURE_BUTTON']
DONATE_BUTTON = CONFIG['MESSAGES']['DONATE_BUTTON']
CONTACT_BUTTON = CONFIG['MESSAGES']['CONTACT_BUTTON']

# Configure logging
logging.basicConfig(level=logging.INFO)

# global variables
TOTAL_IMAGES = 0
COUNT_IMAGES = 0
IMAGES = None

async def main(msg):
    """
    main function.
    sorry, pep8 requires a comment here :)
    """

    chat_id = msg['chat']['id']
    command = msg['text']

    if command.find("/help") != -1:
        await BOT.sendMessage(chat_id, HELP)
    elif command.find("/donate") != -1 or command.find(DONATE_BUTTON) != -1:
        await BOT.sendPhoto(chat_id, DONATE_PICTURE, caption=DONATE, parse_mode='Markdown')
    elif command.find("/contacts") != -1 or command.find(CONTACT_BUTTON) != -1:
        await BOT.sendMessage(chat_id, CONTACTS)
    # counting unique users
    elif command.find("/count") != -1:
        logfile = open(CONFIG['SYSTEM']['DB_WRITE_COMMANDS'], 'r')
        logfile_content = logfile.read()
        logfile.close()
        num_of_uniq_users = len(set(re.findall(r'd+', logfile_content)))
        await BOT.sendMessage(chat_id, str(num_of_uniq_users))
        return
    else:
        photo_url = give_photo(TAG)
        markup = ReplyKeyboardMarkup(keyboard=[
            [dict(text=PICTURE_BUTTON)],
            [DONATE_BUTTON, KeyboardButton(text=CONTACT_BUTTON)],
        ], resize_keyboard=True)
        LOG.write("%s\n" % (chat_id))
        LOG.flush()
        await BOT.sendPhoto(chat_id, photo_url, caption=DESCRIPTION_PICTURE, reply_markup=markup)

 		#
 		# send only links
		#
		#await BOT.sendMessage(chat_id, text='[link](%s)\nGet more @catzcatzcatzbot 😺' % give_photo(),
		#reply_markup=markup, parse_mode= 'Markdown')

def give_photo(tag):
    """
    This function receives the tag and returns the image
    """

    global COUNT_IMAGES
    global IMAGES
    global TOTAL_IMAGES

    if COUNT_IMAGES < TOTAL_IMAGES - 1:
        COUNT_IMAGES += 1
    else:
        IMAGES = ie.tag_images(tag).data
        TOTAL_IMAGES = len(IMAGES)
        COUNT_IMAGES = 0

    print(COUNT_IMAGES)

    return IMAGES[COUNT_IMAGES]

# bot activation
BOT = telepot.aio.Bot(CONFIG['SYSTEM']['BOT_API'])

# creating a task list
LOOP = asyncio.get_event_loop()
LOOP.create_task(BOT.message_loop({'chat': main}))

print('Listening ...')


LOG = open(CONFIG['SYSTEM']['DB_WRITE_COMMANDS'], 'a')
print("read file for write")


try:
    LOOP.run_forever()
except KeyboardInterrupt:
    pass
finally:
    LOOP.stop()
    LOOP.close()
