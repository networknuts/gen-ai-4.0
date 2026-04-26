from openai import OpenAI
from dotenv import load_dotenv

# SETUP THE ENVIRONMENT

load_dotenv()
client = OpenAI()

def transcribe(audio_file):
    """
    Sends an audio file to openai gpt-4.0 transcribe model
    and returns the converted text of the audio file.
    """
    with open(audio_file,"rb") as audio_file_path:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file_path
        )
        return response.text 
    
audio_file = "audio_chunk_0.wav"

text = transcribe(audio_file)

f = open("raw_audio_file.txt","w")
f.write(text)
f.close()