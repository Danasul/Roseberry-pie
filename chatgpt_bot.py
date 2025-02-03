import os
import openai
import time
import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voice = engine.getProperty('voices')[0]
engine.setProperty('voice', voice.id)

# List available devices
print("Available devices:")
print(sd.query_devices())

# Automatically set the default input/output device
try:
    devices = sd.query_devices()
    input_device_name = "USB PnP Sound Device"
    output_device_name = "HP Speaker 400"

    input_device = next((i for i, d in enumerate(devices) if input_device_name in d["name"]), None)
    output_device = next((i for i, d in enumerate(devices) if output_device_name in d["name"]), None)

    if input_device is not None:
        sd.default.device = (input_device, output_device)
        print(f"Using input device: {input_device_name} (ID: {input_device})")
    else:
        print("⚠️ Warning: Input device not found, using default.")

    if output_device is not None:
        print(f"Using output device: {output_device_name} (ID: {output_device})")
    else:
        print("⚠️ Warning: Output device not found, using default.")

except Exception as e:
    print(f"Error setting default devices: {e}")

# Function to convert text to speech
def speak(text):
    print(f"GPT: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to listen for a wake word ("hi")
def listen_for_wake_word():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Waiting for 'hi'...")
        while True:
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio).lower()
                print(f"You said: {text}")
                if "hi" in text:
                    speak("Hi, I am your voice assistant. How can I help?")
                    listen_and_respond()
                    break
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return None

# Function to listen and respond to the user
def listen_and_respond():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Listening...")
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio).lower()
                print(f"You said: {text}")

                if "exit" in text:
                    print("Goodbye!")
                    speak("Goodbye!")
                    break

                # Get response from ChatGPT
                response = chat_with_gpt(text)
                speak(response)

            except sr.UnknownValueError:
                print("Could not understand the audio")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")

# Function to send input to ChatGPT
def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error communicating with OpenAI API: {e}"

# Main loop: Wait for "hi" before starting conversation
if _name_ == "_main_":
    listen_for_wake_word()
