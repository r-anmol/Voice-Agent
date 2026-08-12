import speech_recognition as sr
import asyncio

from .graph import run_kavya_turn  # 👈 pull the helper, not just the graph
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

openai = AsyncOpenAI()
USER_ID = "Anmol"


async def tts(text: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="Speak in an affectionate, loving, slightly dramatic desi-girlfriend manner.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


def main():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2

        while True:
            print("🎤 Speak something...")
            audio = r.listen(source)

            try:
                user_text = r.recognize_google(audio)
            except Exception as e:
                print("STT error:", e)
                continue

            print("YOU:", user_text)

            # 👉 this does: search mem0 -> run graph -> write mem0
            assistant_text = run_kavya_turn(user_text, user_id=USER_ID)

            if assistant_text.strip():
                try:
                    asyncio.run(tts(assistant_text))
                except Exception as e:
                    print("TTS error:", e)


if __name__ == "__main__":
    main()
