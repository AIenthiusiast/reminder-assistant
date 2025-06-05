import openai
import os
import io
from datetime import datetime

# 🔐 API-Key laden
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔧 Konfiguration
ASSISTANT_ID = "asst_Mv1kuOUTnrmxvLvE9AsdL3Lx"
VECTOR_STORE_ID = "vs_68404a3fba4c8191abd0be2dd656b8fc"

# 🖐️ Begrüßung
print("\n💬 Willkommen bei SmartReminderGPT!")
print("Du kannst jederzeit Erinnerungen eingeben.")
print("Beispiel: 'Erinnere mich am Freitag um 8 Uhr an Lisa schreiben.'")
print("Zum Beenden: 'exit'\n")

# 🪢 Hauptloop
while True:
    user_input = input("> ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Auf Wiedersehen!")
        break

    # 🧵 Thread starten
    thread = openai.beta.threads.create()

    # Nachricht an Thread anhängen
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    # ⏳ GPT starten
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )

    # 🕒 Warten, bis GPT fertig ist oder Tool aufgerufen wird
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )

        if run_status.status == "completed":
            break

        elif run_status.status == "requires_action":
            tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
            function_name = tool_call.function.name
            arguments = eval(tool_call.function.arguments)

            if function_name == "save_reminder":
                reminder_text = arguments["reminder_text"]
                reminder_time = arguments["reminder_time"]

                # 📄 Dateiinhalt erzeugen
                content = f"Reminder: {reminder_text}\nTime: {reminder_time}"
                file_buffer = io.BytesIO(content.encode("utf-8"))

                # 📤 Hochladen bei OpenAI
                uploaded_file = openai.files.create(
                    file=("reminder.txt", file_buffer),
                    purpose="assistants"
                )

                # 🧠 In Vector Store speichern
                openai.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=VECTOR_STORE_ID,
                    files=[("reminder.txt", io.BytesIO(content.encode("utf-8")))]
                )

                print("✅ Erinnerung im Vector Store gespeichert!")

                # GPT mitteilen, dass Tool-Ausführung fertig
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": tool_call.id,
                            "output": "Erinnerung erfolgreich im Vector Store gespeichert."
                        }
                    ]
                )
                break

    # 🤖 Ausgabe von GPT anzeigen
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print("🤖:", msg.content[0].text.value)
            break
