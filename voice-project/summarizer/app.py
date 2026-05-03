from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI()

@app.post("/summarize")
def summarize(data: dict):
    text = data["text"]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Convert the transcript into a clean, professional summary with bullet points and sections."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    summary = response.choices[0].message.content

    print("\n=== FINAL SUMMARY ===\n")
    print(summary)

    return {"summary": summary}