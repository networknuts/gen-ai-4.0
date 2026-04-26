from openai import OpenAI
from dotenv import load_dotenv

# SETUP ENVIRONMENT
load_dotenv()
client = OpenAI()

f = open("prompt.txt","r")
SYSTEM_PROMPT = f.read()
f.close()

def summarize(raw_meeting_notes):
    response = client.responses.create(
        model="gpt-5-nano",
        instructions=SYSTEM_PROMPT,
        input=raw_meeting_notes
    )
    return response.output_text

f = open("raw_audio_file.txt","r")
raw_meeting_notes = f.read()
f.close()

summary = summarize(raw_meeting_notes)
print(summary)