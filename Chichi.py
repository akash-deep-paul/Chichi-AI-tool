import requests
import os
import re
import webbrowser
import time
from datetime import datetime
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import pyttsx3
import random

# ---------------- VOICE ---------------- #

def init_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 1.0)
    return engine

def say(text):
    print("Chichi:", text)
    try:
        engine = init_engine()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except:
        pass

# ---------------- YOUTUBE ---------------- #

video_list = []
video_index = 0

def search_youtube(query):
    global video_list, video_index

    url = f"https://www.youtube.com/results?search_query={query}"
    html = requests.get(url).text

    video_list = re.findall(r"watch\?v=(\S{11})", html)
    video_list = list(dict.fromkeys(video_list))[:5]

    video_index = 0
    return play_video()

def play_video():
    global video_index

    if video_index < len(video_list):
        webbrowser.open(f"https://www.youtube.com/watch?v={video_list[video_index]}&autoplay=1")
        return "Playing"
    return "No more videos"

def next_video():
    global video_index

    os.system("taskkill /im chrome.exe /f")
    os.system("taskkill /im msedge.exe /f")
    time.sleep(1)

    video_index += 1
    return play_video()

# ---------------- GOOGLE ---------------- #

def open_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return "Opening"

# ---------------- WIKIPEDIA ---------------- #

def open_wikipedia(query):
    query = query.replace(" ", "_")
    webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
    return "Opening"

# ---------------- TIME / DATE ---------------- #

def get_time():
    return datetime.now().strftime("It's %I:%M %p")

def get_date():
    return datetime.now().strftime("Today is %d %B %Y")

# ---------------- CALCULATOR ---------------- #

def calculate_expression(user):
    try:
        expr = user.replace("calculate", "").strip()
        expr = expr.replace("plus", "+").replace("minus", "-")
        expr = expr.replace("into", "*").replace("divided by", "/")

        if not re.match(r'^[0-9+\-*/(). ]+$', expr):
            return "Invalid"

        result = eval(expr, {"__builtins__": None}, {})
        return f"{result}"
    except:
        return "Error"

# ---------------- OPEN APPS ---------------- #

APPS = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "notepad": "notepad.exe",
    # add more later like:
    # "fortnite": "C:\\Users\\YourName\\Desktop\\fortnite.lnk"
}

def open_app(app_name):
    app_name = app_name.strip()

    if not app_name:
        return "What should I open?"

    if app_name in APPS:
        path = APPS[app_name]

        if path.startswith("http"):
            webbrowser.open(path)
        else:
            os.startfile(path)

        return "Opening"

    return "I don't know that app"

# ---------------- CLOSE ---------------- #

def close_all():
    os.system("taskkill /im chrome.exe /f")
    os.system("taskkill /im msedge.exe /f")
    return "Closed"

# ---------------- TRIGGER ---------------- #

TRIGGERS = ["chichi","chi chi","chechi","chici","shishi","tithi","trichi","trichy","tc","cg","cici"]

def is_triggered(user):
    user_clean = user.replace(" ", "")
    return any(t.replace(" ", "") in user_clean for t in TRIGGERS)

def remove_trigger(user):
    for t in TRIGGERS:
        user = re.sub(rf"\b{t}\b", "", user)
    return user.strip()

# ---------------- INTENT ---------------- #

def detect_intent(user):
    if "show me" in user:
        return "YOUTUBE"

    elif "open" in user:
        return "OPEN"

    elif "weather" in user:
        return "WEATHER"

    elif "price" in user:
        return "PRICE"

    elif "tell me about" in user:
        return "WIKI"

    elif "time" in user:
        return "TIME"

    elif "date" in user:
        return "DATE"

    elif "calculate" in user:
        return "CALCULATE"

    elif "next" in user:
        return "NEXT"

    elif any(x in user for x in ["close", "stop"]):
        return "CLOSE"

    return "UNKNOWN"

# ---------------- LISTEN ---------------- #

def listen():
    fs = 16000
    threshold = 100
    silence_limit = 0.5

    print("🎤 Listening...")

    audio_data = []
    silent_chunks = 0

    with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
        while True:
            chunk, _ = stream.read(1024)
            audio_data.append(chunk)

            volume = np.linalg.norm(chunk)

            if volume < threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks > int(silence_limit * fs / 1024):
                break

            if len(audio_data) > int(10 * fs / 1024):
                break

    recording = np.concatenate(audio_data, axis=0)
    audio_raw = recording.tobytes()
    audio_data_obj = sr.AudioData(audio_raw, fs, 2)

    r = sr.Recognizer()
    try:
        text = r.recognize_google(audio_data_obj)
        print("You said:", text)
        return text.lower()
    except:
        return ""

# ---------------- MAIN ---------------- #

def main():
    say("Ready")

    while True:
        user = listen()

        if not user:
            continue

        if not is_triggered(user):
            continue

        user = remove_trigger(user)

        intent = detect_intent(user)

        # -------- ACTION -------- #

        if intent == "YOUTUBE":
            query = user.replace("show me", "").strip()
            if not query:
                say("What should I show?")
            else:
                say(search_youtube(query))

        elif intent == "OPEN":
            app = user.replace("open", "").strip()
            say(open_app(app))

        elif intent == "WEATHER":
            say(open_google(user))

        elif intent == "PRICE":
            say(open_google(user))

        elif intent == "WIKI":
            query = user.replace("tell me about", "").strip()
            if query:
                say(open_wikipedia(query))
            else:
                say("Tell me what you want to know")

        elif intent == "TIME":
            say(get_time())

        elif intent == "DATE":
            say(get_date())

        elif intent == "CALCULATE":
            say(calculate_expression(user))

        elif intent == "NEXT":
            say(next_video())

        elif intent == "CLOSE":
            say(close_all())

        else:
            say(random.choice([
                "I didn't understand",
                "Say that again",
                "Try another way"
            ]))

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    main()