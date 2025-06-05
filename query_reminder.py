import openai
import os
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

# Deine Assistant-ID (von vorher)
assistant_id = "asst_Mv1kuOUTnrmxvLvE9AsdL3Lx"

# Neuen Thread starten
thread = openai.beta.threads.create()

# Nutzerfrage hinzufügen – GPT soll eine gespeicherte Erinnerung finden
openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Steht etwas an demnächst?"
)

# Assistant starten
run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id
)

# Warten bis abgeschlossen
while True:
    run_status = openai.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    if run_status.status == "completed":
        break
    print("⏳ Warten...")
    time.sleep(1)

# Antwort anzeigen
messages = openai.beta.threads.messages.list(thread_id=thread.id)
latest_message = messages.data[0]

print("\n💬 GPT-Antwort:")
for content in latest_message.content:
    if content.type == "text":
        print(content.text.value)
