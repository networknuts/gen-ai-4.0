from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

f = open("cot.txt","r")
system_prompt = f.read()
f.close()

user_query = input("Business Idea: ")

response = client.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=user_query
)

print("\nAI Expert Panel Response: \n")
print(response.output_text)