from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

f = open("few-shot-prompt.txt","r")
system_prompt = f.read()
f.close()

user_query = input("Symptoms: ")

response = client.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=user_query
)

print("AI Medical Response: \n")
print(response.output_text)