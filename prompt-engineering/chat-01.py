from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

f = open("one-shot-prompt.txt","r")
system_prompt = f.read()
f.close()

user_query = input("Human: ")

response = client.responses.create(
    model="gpt-5-nano",
    instructions=system_prompt,
    input=user_query
)

print("AI Response: \n")
print(response.output_text)