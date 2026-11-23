import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import os
from datetime import datetime
import cv2
import warnings
from bs4 import XMLParsedAsHTMLWarning
from groq import Groq
from dotenv import load_dotenv
import pyperclip
import pyautogui  # For controlling keyboard
import time       # For adding delays

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# --- SECURELY CONFIGURE THE GEMINI API ---
# --- GROQ API CONFIGURATION ---
load_dotenv()

try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in .env")

    client = Groq(api_key=GROQ_API_KEY)
    GROQ_ENABLED = True

except Exception as e:
    print(f"Groq configuration error: {e}")
    GROQ_ENABLED = False

# Initialize recognizer and text-to-speech engine
recogniser = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()


def ask_gemini(command):
    """Sends a command to Groq and returns the AI response."""

    if not GROQ_ENABLED:
        return "My AI brain is currently unavailable. Please check the Groq API configuration."

    try:
        print(f"Sending to Groq: {command}")

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, an intelligent desktop AI assistant. "
                        "Respond naturally, clearly and concisely. "
                        "You are helpful, professional and friendly."
                    )
                },
                {
                    "role": "user",
                    "content": command
                }
            ],
            temperature=0.6,
            max_completion_tokens=1024
        )

        answer = response.choices[0].message.content

        return answer.replace("*", "").replace("`", "")

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Sorry, I am having trouble connecting to my AI brain right now."


def get_weather(place="delhi"): # The default place is now your location
    """Fetches weather information from wttr.in."""
    try:
        url = f"https://wttr.in/{place}?format=%C+%t"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        report = res.text.strip()
        return f"The weather in {place} is currently {report}"
    except Exception as e:
        return f"Error fetching weather: {e}"

def play_song_on_youtube(song):
    """Searches for a song on YouTube and opens the first result."""
    query = urllib.parse.quote(song)
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        response = requests.get(url).text
        video_ids = re.findall(r"watch\?v=(\S{11})", response)
        if video_ids:
            first_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            webbrowser.open(first_video_url)
        else:
            speak("Sorry, I could not find that song on YouTube.")
    except Exception as e:
        print(f"Error playing song: {e}")
        speak("Sorry, I ran into an error trying to play the song.")

def open_camera_and_capture():
    """Opens the default camera and takes a picture."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Sorry, I couldn't access the camera.")
            return
        speak("Opening camera. Smile!")
        ret, frame = cap.read()
        if ret:
            filename = "captured_image.jpg"
            cv2.imwrite(filename, frame)
            speak("Photo captured successfully!")
            os.startfile(filename)
        else:
            speak("Failed to capture the photo.")
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Camera error: {e}")
        speak("Something went wrong with the camera.")

def get_news():
    try:
        url = "https://news.google.com/rss"   # Google News RSS feed
        res = requests.get(url, timeout=5)
        res.raise_for_status()

        try:
            soup = BeautifulSoup(res.text, "lxml-xml")   # best for RSS
        except Exception:
            soup = BeautifulSoup(res.text, "html.parser")

        items = soup.find_all("item")[:5]  # get top 5 news
        headlines = [item.title.get_text() for item in items]

        if not headlines:
            return ["Sorry, I couldn't fetch the news."]
        return headlines

    except Exception as e:
        return [f"Error while fetching news: {str(e)}"]
# --- Process the spoken command ---
def processcommand(c):
    """Processes the user's voice command."""
    c = c.lower()

    # --- Search Commands with Auto-Paste ---
    if "search on google" in c or c.startswith("google search") or "google" in c:
        query = c.replace("search on google", "").replace("google search", "").replace("google","").strip()
        speak(f"Searching on Google for {query}")
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        return

    elif "search on chat gpt" in c or c.startswith("chat gpt search") or "chat gpt" in c:
        query = c.replace("search on chat gpt", "").replace("chat gpt search", "").replace("chat gpt","").strip()
        pyperclip.copy(query)
        speak(f"Searching on chat gpt for {query}")
        webbrowser.open("https://chatgpt.com/")
        time.sleep(5)  # Wait for the page to load
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        speak("I have pasted and submitted your request.")
        return
        
    elif "search on gemini" in c or c.startswith("gemini search") or "gemini" in c:
        query = c.replace("search on gemini", "").replace("gemini search", "").replace("gemini","").strip()
        pyperclip.copy(query)
        speak(f"Searching on gemini for {query}")
        webbrowser.open("https://gemini.google.com/")
        time.sleep(5)  # Wait for the page to load
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        speak("I have pasted and submitted your request.")
        return

    # --- "Open Website" Commands ---
    elif "open google" in c:
        webbrowser.open("https://www.google.com")
        speak("Opening google")
    elif "open youtube" in c:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")
    elif "open facebook" in c:
        webbrowser.open("https://www.facebook.com/")
        speak("Opening Facebook")
    elif "open instagram" in c:
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram")
    elif "open spotify" in c:
        webbrowser.open("https://open.spotify.com")
        speak("Opening Spotify")
    elif "open whatsapp" in c:
        webbrowser.open("https://web.whatsapp.com/")
        speak("Opening WhatsApp")
    elif "open wikipedia" in c:
        webbrowser.open("https://www.wikipedia.org/")
        speak("Opening Wikipedia")
    elif "open linkedin" in c:
        webbrowser.open("https://www.linkedin.com/feed/")
        speak("Opening LinkedIn")
    elif "open chat gpt" in c:
        webbrowser.open("https://chatgpt.com/")
        speak("Opening ChatGPT")

    # --- Utility Commands ---
    elif c.startswith("play"):
        song = c.replace("play", "").strip()
        speak(f"Playing {song}")
        play_song_on_youtube(song)
    elif "news" in c:
        speak("Here are the top news headlines.")
        news_list = get_news()
        for headline in news_list:
            speak(headline)
    elif "time" in c:
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
    elif "date" in c:
        current_date = datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif "weather" in c:
        # Extracts the city name from your voice command
        place = c.replace("weather in", "").replace("what's the weather in", "").replace("weather", "").strip()
        
        # If you said a city, use it. If not, use the default.
        if place:
            report = get_weather(place)
        else:
            report = get_weather("Sumerpur") # Your default location
        speak(report)
    elif "take a picture" in c or "click a photo" in c or "open camera" in c or "take picture" in c or "open a camera" in c:
        open_camera_and_capture()
        
    # --- Fallback to AI for general questions ---
    else:
        output = ask_gemini(c)
        speak(output)

# --- Main loop ---
if __name__ == "__main__":
    speak("Initializing Jarvis")
    while True:
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("\nListening for wake word 'Jarvis'...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5, phrase_time_limit=4)
                word = r.recognize_google(audio)
                if word and word.lower() == "jarvis":
                    speak("Yes, i'm here")
                    with sr.Microphone() as source2:
                        print("Jarvis activated...")
                        audio_command = r.listen(source2, timeout=7, phrase_time_limit=10)
                        command = r.recognize_google(audio_command)
                        if command:
                            print(f"You said: {command}")
                            processcommand(command)
        except sr.WaitTimeoutError:
            pass

        except sr.UnknownValueError:
            pass

        except KeyboardInterrupt:
            print("\nJARVIS stopped by user.")
            speak("Gooodbyee!")
            break

        except Exception as e:
            print(f"An error occurred: {e}")