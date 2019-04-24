#!/usr/bin/env python
import logging
import os
import string
import re
import random

from apscheduler.schedulers.background import BackgroundScheduler
import flask
import pyphen
from PyLyrics import *

import messages
import messaging
import helper


'''Logger'''
log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)


app = flask.Flask(__name__)

RESPONSE_DIR = "long_responses"

previous_sender_id = None


@app.route('/', methods=['GET', 'POST'])
def index():
    #return flask.abort(403)
    
    if flask.request.method == 'GET':
        return flask.send_from_directory(directory='static', filename='index.html')

    message = flask.request.form["message"]
    link_pattern = r'\w+\.\w+'

    if re.match(link_pattern, message):
        return "please don't send links"
    
    if message[-1] != "?":
        return "you must submit a question"

    messaging.send_message("{}\nsubmission link: https://globbot.herokuapp.com/".format(message))
    return flask.redirect('https://globbot.herokuapp.com/')


@app.route('/incoming_message', methods=['GET', 'POST'])
def incoming_message():
    if flask.request.method == 'GET':
        return 'page loaded'

    print("in incoming_message")
    print("incoming_message got: {}".format(flask.request.data))

    message_dict = flask.request.get_json(force=True, silent=True)
    if not message_dict:
        print("ERROR with message format, data is: {}".format(flask.request.data))
        return 'bad message format'

    if message_dict["sender_type"] != "user":
        return "ignoring bot messages"

    dic = pyphen.Pyphen(lang='en')

    message = message_dict["text"]
    username = message_dict["name"]
    user_id = message_dict["user_id"]
    conversation_id = message_dict["group_id"]
    message_id = message_dict["id"]
    sender_id = message_dict["sender_id"]

    austin_sender_id = "37816131"

    # bot commands
    if (message.startswith("@bot")):
        full_command = message.split()

        if len(full_command) < 2:
            return 'invalid bot command'

        command = full_command[1].lower()
        if command in ['help', 'commands', 'command', 'options', 'option']:
            help_message = "Commands:\n'@bot lyrics <Artist>, <Song>'\n'@bot brother'\n'@bot accolades'\n'@bot repost'\n'@bot slatt'\n'@bot nuke'\n'koalas'"
            messaging.send_message(help_message)
        elif command == 'lyrics':
            try:
                artist_song = message[len("@bot lyrics "):]
                lyrics_args = artist_song.split(',')
                artist = lyrics_args[0]
                song = lyrics_args[1][1:]
                print("lyrics looking for: {}, {}".format(artist, song))
                messaging.send_message(PyLyrics.getLyrics(artist, song))
            except ValueError:
                messaging.send_message(
                    "Song ({}) or Singer ({}) does not exist or the API does not have Lyrics".format(song, artist))
        elif command == 'brother':
            messaging.send_message("Hell yeah, brother!")
        elif command == 'accolades':
            messaging.send_message(
                "I'm more successful, I have more accolades, I'm more charismatic, and more people know who I am. All because of my brain and how I use it, cole. U know if u pay attention maybe u could learn something.")
        elif command == 'repost':
            messaging.send_message(
                "*Sniff sniff* What's this? OwO IS THIS A REPOST?")
        elif command == 'slatt':
            messaging.send_message("Slime Love All The Time")
        elif command == 'nuke':
            for i in range(10):
                messaging.send_message("This is how the world ends, not with a bang but with roboto")
        elif command == "koalas":
            messaging.send_message(helper.get_file_text(os.path.join(RESPONSE_DIR, "koalas.txt")))
        else:
            messaging.send_message("invalid command")
        return ''
    # Case and punctuation sensitive repsonses
    if "Bush" in message:
        messaging.send_message("George W. Bush, best president")
        return ''
    elif message[-1] == "*" and previous_sender_id != sender_id:
        messaging.send_message(helper.get_file_text(os.path.join(RESPONSE_DIR, "mistake.txt")))
        previous_sender_id = sender_id
        return ''
    previous_sender_id = sender_id
    # remove punctuation and make lowercase
    message = re.sub(r'[^\w\s]', '', message).lower()
    print(message)
    # responses to single word messages
    if message == "nice":
        messaging.send_message("Yeah, nice.")
    elif message == "wow":
        messaging.send_message("https://media1.fdncms.com/stranger/imager/u/original/25961827/28378083_1638438199580575_8366019535260245188_n.jpg")
    # responses to substrings
    else:
        # multi-word strings
        if "what time" in message:
            messaging.send_message("Time to get a watch!")
            return 'message sent'
        elif "que hora" in message:
            messaging.send_message("Es hora obtener un reloj!")
            return 'message sent'

        # message contains single key-word
        for word in message.split():

            if word in ['updog', 'ligma', 'sugma']:
                messaging.send_message("What's {}?".format(word))
                return 'message sent'

            if word in ["u", "ur"] and sender_id == austin_sender_id:
                if word == "u":
                    messaging.send_message(
                        "You said \"{},\" did you mean \"you?\"".format(word))
                else:
                    messaging.send_message(
                        "You said \"{},\" did you mean \"your?\"".format(word))
                return 'message sent'

            syllables = dic.inserted(word).split('-')
            print(syllables)
            if (random.randrange(3) == 0 and syllables[-1] == 'er'
               and word not in ['other', 'another', 'ever', 'never', 'together', 'whatever', 'whenever', 'earlier', 'whomever', 'whoever']):
                messaging.send_message(
                    "{}? I barely even know her!".format(word.capitalize()))
                return 'message sent'

    return 'good'


def keep_app_awake():
    requests.get("https://globbot.herokuapp.com/")


if __name__ == '__main__':

    # get lyrics once to get rid of warning in source code
    PyLyrics.getLyrics('Riff Raff', 'How To Be The Man')

    scheduler = BackgroundScheduler()
    tz = 'US/Eastern'
    scheduler.add_job(messages.LA_time, trigger='cron',
                      hour=12, minute=8, timezone=tz)
    scheduler.add_job(messages.five_o_clock, trigger='cron',
                      hour=5, timezone=tz)
    scheduler.add_job(messages.meat_show, trigger='cron',
                      month=2, day=14, hour=9, 
                      timezone=tz)
    scheduler.add_job(messages.rip_mouse, trigger='cron',
                      month=4, day=23, hour=12,
                      timezone=tz)
    scheduler.add_job(keep_app_awake, 'interval', minutes=20, timezone=tz)
    scheduler.start()

# Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
