import os
import pyaudio
import wave
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
import openai

# Set up API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Google Cloud Speech-to-Text settings
client = speech.SpeechClient.from_service_account_json(google_credentials_path)
audio = speech.RecognitionAudio(uri="gs://your-bucket-name/output.wav")
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
)

# Google Cloud Text-to-Speech settings
tts_client = texttospeech.TextToSpeechClient.from_service_account_json(google_credentials_path)
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    ssml_gender=texttospeech.SsmlVoiceGender.MALE,
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio():
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript

def generate_response(user_input):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_input,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def synthesize_speech(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("response.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("mpg321 response.mp3")

if _name_ == "_main_":
    record_audio()
    user_input = transcribe_audio()
    print(f"User: {user_input}")
    bot_response = generate_response(user_input)
    print(f"Bot: {bot_response}")
    synthesize_speech(bot_response)