from messaging import send_message
import random

def LA_time():
    if random.randrange(7) == 0:
	    send_message("9:08, LA time")

def meat_show():
	send_message("welcome to the meat show")

def five_o_clock():
    if random.randrange(30) == 0:
	    send_message("It's 5 o'clock in the morning")

def rip_mouse():
    send_message("RIP glue trap mouse, 4/23/19")

def test_scheduler():
	send_message("scheduled message in memory of JP")
	