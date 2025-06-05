import openai
import os
import json
from functions import save_reminder
import time

# 🔐 API-Key laden
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔧 Konfiguration
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Schema für Tool-Funktion
function_schema = {
    "name": "save_reminder",
    "description": "Speichert eine Erinnerung im Vector Store",
    "parameters": {
        "type": "object",
        "properties": {
            "reminder_text": {"type": "string", "description": "Text der Erinnerung"},
            "reminder_time": {"type": "string", "description": "Zeitpunkt im ISO-Format"},
        },
        "required": ["reminder_text", "reminder_time"],
    },
}

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
        tools=[{"type": "function", "function": function_schema}],
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
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "save_reminder":
                reminder_text = arguments["reminder_text"]
                reminder_time = arguments["reminder_time"]

                save_reminder(reminder_text, reminder_time)
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
        time.sleep(1)

    # 🤖 Ausgabe von GPT anzeigen
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print("🤖:", msg.content[0].text.value)
            break
