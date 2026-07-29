import requests
import os
import re
import webbrowser
import time
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import pyttsx3
import random
import keyboard
import feedparser
from datetime import datetime, timedelta, timezone

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

last_news = []
news_page = 0

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

# ---------------- NEWS ---------------- #

WORLD_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.dw.com/xml/rss-en-all",
    "https://www.aljazeera.com/xml/rss/all.xml",
]

INDIA_FEEDS = [
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://indianexpress.com/section/india/feed/",
]

WB_FEEDS = [
    "https://news.google.com/rss/search?q=Kolkata+OR+Howrah&hl=en-IN&gl=IN&ceid=IN:en"
]
    
last_search_results = []
search_index = 0
last_search_query = ""

def get_news(region="world"):
    global last_news, news_page

    last_news = []
    news_page = 0

    if region == "india":
        feeds = INDIA_FEEDS

    elif region == "west bengal":
        feeds = WB_FEEDS

    else:
        feeds = WORLD_FEEDS

    headlines = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:

                title = entry.title.split(" - ")[0]
           
                summary = getattr(entry, "summary", "No details available")

                summary = re.sub(r'<.*?>', '', summary)
                summary = summary.replace("&nbsp;", " ")
                summary = summary.replace("&#39;", "'")
                summary = summary.replace("&quot;", '"')


                try:
                    published = datetime(*entry.published_parsed[:6])

                    diff = datetime.now() - published

                    hours = int(diff.total_seconds() / 3600)

                    if hours < 1:
                        hours_text = "Less than 1 hour ago"
                    else:
                        hours_text = f"{hours} hours ago"

                except:
                    hours_text = "Recently"

                last_news.append({
                    "title": title,
                    "link": getattr(entry, "link", ""),
                    "summary": summary,
                    "hours": hours_text
                })

                if title not in headlines:
                    headlines.append({
                     "hours": hours_text,
                     "title": title
                    })

        except:
            pass

    if not headlines:
        return f"No {region} news found"
    

    result = ""

    for i, news in enumerate(headlines[:5], start=1):
       result += f"News {i}. {news['hours']}. {news['title']}. "

    return result
      
def more_news():
    global last_news, news_page

    news_page += 1

    start = news_page * 5
    end = start + 5

    more = last_news[start:end]

    if not more:
        return "No more news available"

    result = ""

    for i, news in enumerate(more, start=start+1):
       result += f"News {i}. {news['hours']}. {news['title']}. "

    return result

def news_details(number):

    global last_news

    index = number - 1

    if index < 0 or index >= len(last_news):
        return "News not found"

    article = last_news[index]

    return article.get("summary", "No details available")


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

    elif "west bengal news" in user:
        return "WB_NEWS"

    elif "india news" in user:
        return "INDIA_NEWS"

    elif "world news" in user:
        return "WORLD_NEWS"

    elif "more headlines" in user or "more headlines" in user:
        return "MORE_NEWS"

    elif "tell me more about news" in user:
        return "NEWS_DETAILS" 

    elif "find news" in user:
        return "FIND_NEWS"

    elif "news" in user:
        return "NEWS"

    elif "anything else" in user:
        return "NEXT_ARTICLE"

    elif any(x in user for x in ["close", "stop"]):
        return "CLOSE"

    return "UNKNOWN"

# ---------------- LISTEN ---------------- #

def listen():
    fs = 16000

    print("Hold CTRL + SHIFT and speak...")

    while not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift")):
        time.sleep(0.05)

    print("🎤 Recording...")

    audio_data = []

    with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:

        while keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift"):
            chunk, _ = stream.read(1024)
            audio_data.append(chunk)

    print("🛑 Recording stopped")

    if not audio_data:
        return ""

    recording = np.concatenate(audio_data, axis=0)

    audio_raw = recording.tobytes()
    audio_data_obj = sr.AudioData(audio_raw, fs, 2)

    r = sr.Recognizer()

    try:
        text = r.recognize_google(audio_data_obj)
        print("You said:", text)
        return text.lower()

    except Exception as e:
        print("speech Error:", e)
        return ""

def find_news(topic):
    global last_search_results
    global search_index
    global last_search_query
    
    results = []

    for url in WORLD_FEEDS + INDIA_FEEDS + WB_FEEDS:

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:

                title = entry.title

                summary = getattr(entry, "summary", "")

                text = (title + " " + summary).lower()

                if topic.lower() in text:

                    try:
                        published = datetime(*entry.published_parsed[:6])

                        diff = datetime.now() - published

                        hours = int(diff.total_seconds() / 3600)

                    except:
                        hours = "unknown"

                    results.append({
                        "hours": hours,
                        "title": title
                    })

        except:
            pass

        if results:

            results.sort(key=lambda x: x["hours"])

            last_search_results = results
            search_index = 0
            last_search_query = topic

            first = results[0]

            return f'{first["hours"]} hours ago. {first["title"]}'

    return "No recent news found"

def next_search_result():

    global last_search_results
    global search_index

    search_index += 1

    if search_index >= len(last_search_results):
        return "No more related articles found"

    item = last_search_results[search_index]

    return f'{item["hours"]} hours ago. {item["title"]}'

# ---------------- MAIN ---------------- #

def main():
    say("Ready")

    while True:
        user = listen()

        if not user:
            continue

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
        
        elif intent == "MORE_NEWS":
            say(more_news())
         
        elif intent == "NEWS_DETAILS":

           match = re.search(r"news\s+(\d+)", user)

           if match:
               number = int(match.group(1))
               say(news_details(number))
           else:
               say("Which news number?")

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

        elif intent == "WORLD_NEWS":
            say(get_news("world"))

        elif intent == "FIND_NEWS":

            topic = user.replace("find news", "").strip()

            if topic:
                say(find_news(topic))
            else:
                say("What news should I find?")

        elif intent == "INDIA_NEWS":
            say(get_news("india"))

        elif intent == "WB_NEWS":
            say(get_news("west bengal"))

        elif intent == "NEXT_ARTICLE":
            say(next_search_result())

        elif intent == "NEWS":
            say(get_news("world"))

        else:
            say(random.choice([
                "I didn't understand",
                "Say that again",
                "Try another way"
            ]))

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    main()