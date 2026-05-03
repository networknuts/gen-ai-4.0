from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI
import tempfile
import subprocess
import os
import requests

app = FastAPI()
client = OpenAI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("Client connected 🔥")

    transcripts = []
    buffer = b""           # 🔥 accumulate audio
    chunk_counter = 0      # 🔥 track chunks
    base_chunk = None

    try:
        while True:
            data = await ws.receive()

            # 🔴 STOP condition
            if "text" in data and data["text"] == "STOP":
                print("STOP received")
                break

            if "bytes" not in data:
                continue

            # 🔥 Append chunk
            chunk = data["bytes"]
            if base_chunk is None:
                base_chunk = chunk  # first chunk contains header
            buffer += chunk
            chunk_counter += 1

            # 🔥 Process every 3 chunks (~12 sec)
            if chunk_counter < 3:
                continue

            chunk_counter = 0

            try:
                # -----------------------------
                # 1. Save buffered WebM
                # -----------------------------
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                    f.write(buffer)
                    webm_file = f.name

                buffer = base_chunk  # retain header for next cycle

                # -----------------------------
                # 2. Convert to WAV
                # -----------------------------
                wav_file = webm_file.replace(".webm", ".wav")

                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i", webm_file,
                        "-ar", "16000",
                        "-ac", "1",
                        wav_file
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # -----------------------------
                # 3. Transcribe
                # -----------------------------
                with open(wav_file, "rb") as audio:
                    response = client.audio.transcriptions.create(
                        model="gpt-4o-transcribe",
                        file=audio
                    )

                text = response.text.strip()

                if text:
                    print("Transcript:", text)
                    transcripts.append(text)
                    await ws.send_text(text)

                # cleanup
                os.remove(webm_file)
                os.remove(wav_file)

            except Exception as e:
                print("Chunk processing error:", str(e))
                await ws.send_text("⚠️ Error processing audio chunk")

    except WebSocketDisconnect:
        print("Client disconnected")

    # -----------------------------
    # 🔥 FINAL BUFFER PROCESS (important)
    # -----------------------------
    try:
        if buffer:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                f.write(buffer)
                webm_file = f.name

            wav_file = webm_file.replace(".webm", ".wav")

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", webm_file,
                    "-ar", "16000",
                    "-ac", "1",
                    wav_file
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            with open(wav_file, "rb") as audio:
                response = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio
                )

            text = response.text.strip()

            if text:
                transcripts.append(text)
                await ws.send_text(text)

            os.remove(webm_file)
            os.remove(wav_file)

    except Exception as e:
        print("Final buffer error:", str(e))

    # -----------------------------
    # 🔥 SEND SUMMARY
    # -----------------------------
    try:
        full_text = " ".join(transcripts)

        if full_text.strip():
            print("\n=== FULL TRANSCRIPT ===\n", full_text)

            response = requests.post(
                "http://summarizer:8000/summarize",
                json={"text": full_text},
                timeout=10
            )

            if response.status_code == 200:
                summary = response.json().get("summary", "")

                print("\n=== SUMMARY ===\n", summary)

                await ws.send_text("\n=== FINAL SUMMARY ===")
                await ws.send_text(summary)

            else:
                print("Summarizer error:", response.text)

    except Exception as e:
        print("Final summarization error:", str(e))

    print("Session complete ✅")