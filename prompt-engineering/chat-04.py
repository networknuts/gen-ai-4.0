from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


user_query = input("Human Input: ")

response = client.responses.create(
    model="gpt-5-nano",
    input=[
        {
            "role": "user",
            "content": "hi my name is aryan and i work in devops."
        },
        {
            "role": "assistant",
            "content": "Nice to meet you, Aryan. How can I help you with DevOps today?"
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
)

print("\nAI Response: \n")
print(response.output_text)