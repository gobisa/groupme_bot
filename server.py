#!/usr/bin/env python
"""Server for a GroupMe Bot."""
import logging
import os
#import string
import re
import random
import requests

from apscheduler.schedulers.background import BackgroundScheduler
import flask
import pyphen
from PyLyrics import PyLyrics

import messages
import messaging
import helper


#Logger
LOG = logging.getLogger('apscheduler.executors.default')
LOG.setLevel(logging.DEBUG)  # DEBUG
FMT = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
H = logging.StreamHandler()
H.setFormatter(FMT)
LOG.addHandler(H)


APP = flask.Flask(__name__)

RESPONSE_DIR = "long_responses"

previous_sender_id = None
previous_message = None

peopleId = {
    "alex": "26690961",
    "andrius": "28232254",
    "austin": "37816131",
    "josh": "26690961",
    "keith": "26550236"
}


@APP.route('/', methods=['GET', 'POST'])
def index():
    """Handle website access."""
    # return flask.abort(403)

    if flask.request.method == 'GET':
        return flask.send_from_directory(directory='static', filename='index.html')

    message = flask.request.form["message"]
    link_pattern = r'\w+\.\w+'

    if re.match(link_pattern, message):
        return "please don't send links"

    if message[-1] != "?":
        return "you must submit a question"

    messaging.send_message(
        "{}\nsubmission link: https://globbot.herokuapp.com/".format(message))
    return flask.redirect('https://globbot.herokuapp.com/')


@APP.route('/incoming_message', methods=['GET', 'POST'])
def incoming_message():
    """Handle incoming messages."""
    if flask.request.method == 'GET':
        return 'page loaded'

    print("in incoming_message")
    message_dict = None
    print("incoming_message got: {}".format(flask.request.data))
    #print(flask.request.form)

    if flask.request.data:
        message_dict = flask.request.get_json(force=True, silent=True)
    else:
        message_dict = flask.request.form

    if not message_dict:
        print("ERROR with message format, data is: {}".format(flask.request.data))
        return 'bad message format'

    if message_dict["sender_type"] != "user":
        return "ignoring bot messages"

    dic = pyphen.Pyphen(lang='en')

    message = message_dict["text"].rstrip()
    username = message_dict["name"]
    user_id = message_dict["user_id"]
    conversation_id = message_dict["group_id"]
    message_id = message_dict["id"]
    sender_id = message_dict["sender_id"]

    austin_sender_id = "37816131"

    global previous_message

    # bot commands
    if message.startswith("@bot"):
        full_command = message.split()

        if len(full_command) < 2:
            return 'invalid bot command'

        command = full_command[1].lower()
        if command in ['help', 'commands', 'command', 'options', 'option']:
            help_message = """
                           Commands:\n'@bot lyrics <Artist>, <Song>'
                           \n'@bot brother'
                           \n'@bot accolades'
                           \n'@bot repost'
                           \n'@bot slatt'
                           \n'@bot nuke'
                           \n'@bot koalas'
                           \n'@bot link'
                           \n'@bot owoify'
                           \n'@bot usify'
                           \n'@bot trolled'
                           \n'@bot lucky'
                           """
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
        elif command == 'lucky':
            messaging.send_message("Also I just want you to know I could’ve dropped a nuke on your ass for that comment but I did not. Consider yourself lucky.")
        elif command == 'repost':
            messaging.send_message(
                "*Sniff sniff* What's this? OwO IS THIS A REPOST?")
        elif command == 'slatt':
            messaging.send_message("Slime Love All The Time")
        elif command == 'nuke':
            for i in range(10):
                messaging.send_message(
                    "This is how the world ends, not with a bang but with roboto")
        elif command == "koalas":
            messaging.send_message(helper.get_file_text(
                os.path.join(RESPONSE_DIR, "koalas.txt")))
        elif command == "link":
            messaging.send_message("https://globbot.herokuapp.com/")
        elif command == "owoify":
            messaging.send_message(previous_message.replace("r", "w").replace("l", "w"))
        elif command == "usify":
            messaging.send_message(previous_message.replace(" ", "🇺🇸"))
        elif command == "trolled":
            messaging.send_message(helper.get_file_text(
                os.path.join(RESPONSE_DIR, "trolled.txt")))
        else:
            messaging.send_message("invalid command")
        return ''
    # Case and punctuation sensitive repsonses
    '''
    if "Bush" in message and random.randrange(3) == 0:
        messaging.send_message("George W. Bush, best president")
        return ''
    '''
    '''
    global previous_sender_id
    if len(message) >= 2 and (message[0] == "*" or message[-1] == "*") and previous_sender_id != sender_id:
        
        messaging.send_message(helper.get_file_text(
            os.path.join(RESPONSE_DIR, "mistake.txt")))
        previous_sender_id = sender_id
        return ''
    previous_sender_id = sender_id
    '''
    # remove punctuation and make lowercase
    raw_message = message
    message = re.sub(r'[^\w\s]', '', message).lower().strip()
    print(message)
    # responses to single word messages
    if message == "nice" and random.randrange(3) and sender_id not in [peopleId["alex"]]:
        messaging.send_message("Yeah, nice.")
    elif message == "wow":
        pass
        '''
        messaging.send_message(
            "https://media1.fdncms.com/stranger/imager/u/original/25961827/28378083_1638438199580575_8366019535260245188_n.jpg")
        '''
    # responses to substrings
    else:
        if "'s twisted" in raw_message or "is twisted" in raw_message:
            messaging.send_message(helper.get_file_text(
                os.path.join(RESPONSE_DIR, "joker.txt")))
        # multi-word strings
        if "what time" in message:
            messaging.send_message("Time to get a watch!")
            return 'message sent'
        if "que hora" in message:
            messaging.send_message("Es hora obtener un reloj!")
            return 'message sent'

        # message contains single key-word
        for word in message.split():

            if word in ['updog', 'ligma', 'sugma']:
                messaging.send_message("What's {}?".format(word))
                break

            if word in ["u", "ur"] and sender_id == austin_sender_id and random.randrange(10) == 0:
                messaging.send_message(
                    "You said \"{x},\" did you mean \"yo{x}?\"".format(x=word))
                break

            '''
            syllables = dic.inserted(word).split('-')
            if (random.randrange(100) == 0 and syllables[-1] == 'er'
                    and word not in ['other', 'another', 'ever', 'never', 'together', 'whatever', 'whenever', 'earlier', 'whomever', 'whoever', 'wherever', 'later']):
                messaging.send_message(
                    "{}? I barely even know her!".format(word.capitalize()))
                break
            '''

    previous_message = raw_message
    return 'good'


def keep_app_awake():
    """Ping the server to keep Heroku from putting it to sleep."""
    requests.get("https://globbot.herokuapp.com/")


if __name__ == '__main__':

    # get lyrics once to get rid of warning in source code
    PyLyrics.getLyrics('Riff Raff', 'How To Be The Man')

    SCHEDULER = BackgroundScheduler()
    TZ = 'US/Eastern'
    '''
    SCHEDULER.add_job(messages.LA_time, trigger='cron',
                      hour=12, minute=8, timezone=TZ)
    '''
    #SCHEDULER.add_job(messages.five_o_clock, trigger='cron',
    #                  hour=5, timezone=TZ)
    SCHEDULER.add_job(messages.meat_show, trigger='cron',
                      month=2, day=14, hour=9,
                      timezone=TZ)
    SCHEDULER.add_job(messages.rip_mouse, trigger='cron',
                      month=4, day=23, hour=12,
                      timezone=TZ)
    SCHEDULER.add_job(keep_app_awake, 'interval', minutes=20, timezone=TZ)
    SCHEDULER.start()

    print(helper.get_file_text(os.path.join(RESPONSE_DIR, "joker.txt")))

    # Bind to PORT if defined, otherwise default to 5000.
    PORT = int(os.environ.get('PORT', 5000))
    APP.run(host='0.0.0.0', port=PORT)

