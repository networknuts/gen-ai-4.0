from openai import OpenAI 
from dotenv import load_dotenv 
import requests 
import os 
import json 

# SETUP THE ENVIRONMENT AND THE OPENAI CLIENT
load_dotenv()
client = OpenAI()

# CREATE OUR AI AGENT TOOL 

def get_weather(zipcode):
    apikey = os.getenv("OPENWEATHERMAP_API_KEY")
    countrycode = "in"
    url = f"https://api.openweathermap.org/data/2.5/weather?zip={zipcode},{countrycode}&appid={apikey}"
    result = requests.get(url)
    response = result.json()
    return response 

# TOOL SCHEMA

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a city by providing its zip code",
        "parameters": {
            "type": "object",
            "properties": {
                "zipcode": {
                    "type": "string",
                    "description": "the zip of the location of which you want to get the current weather of"
                },
            },
            "required": ["zipcode"],
        }
    }
]

# FIRST LLM CALL 

response = client.responses.create(
    model="gpt-4.1",
    input="what is the weather in delhi today?",
    tools=tools
)

tool_output = []

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)

        if item.name == "get_weather":
            result = get_weather(args['zipcode'])
            print(result)
            print("------------------")
        else:
            result = "unknown agent called"

        tool_output.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({"result": result})
        })

# SECOND CALL TO LLM WITH RAW RESULTS

final_response = client.responses.create(
    model="gpt-4.1",
    previous_response_id=response.id,
    input=tool_output
)

print(final_response.output_text)