from openai import OpenAI 
from dotenv import load_dotenv 
import requests 
import os 
import json 
import subprocess

# SETUP THE ENVIRONMENT AND THE OPENAI CLIENT
load_dotenv()
client = OpenAI()

# FIRST AI AGENT TOOL: GET WEATHER

def get_weather(zipcode):
    apikey = os.getenv("OPENWEATHERMAP_API_KEY")
    countrycode = "in"
    url = f"https://api.openweathermap.org/data/2.5/weather?zip={zipcode},{countrycode}&appid={apikey}"
    result = requests.get(url)
    response = result.json()
    return response 

# SECOND AI AGENT TOOL: RUN COMMAND

def run_shell(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=True
    )
    return result.stdout

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
    },
    {
        "type": "function",
        "name": "run_shell",
        "description": "Run a shell command by providing the command and receiving its stdout",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "the particular command to execute on the server"
                },
            },
            "required": ["command"],
        }
    }
]

# FIRST LLM CALL 

user_input = input("Human Question: ")

response = client.responses.create(
    model="gpt-4.1",
    input=user_input,
    tools=tools
)

tool_output = []

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)

        if item.name == "get_weather":
            print("RUNNING GET WEATHER AGENT")
            result = get_weather(args['zipcode'])
        elif item.name == "run_shell":
            print("RUNNING RUN SHELL TOOL")
            result = run_shell(args['command'])
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