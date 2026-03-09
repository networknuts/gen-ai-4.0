from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

user_query = input("Human: ")

response = client.responses.create(
    model="gpt-5-nano",
    input=user_query
)

print("AI Response: \n")
print(response.output_text)