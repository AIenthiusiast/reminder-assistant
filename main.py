import openai
import os
import time
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

# Deine Assistant-ID hier einfügen
ASSISTANT_ID = "asst_CZ6DXX1CVriQy4GfEc8xISwi"

# Schritt 1: Thread erstellen
thread = openai.beta.threads.create()

# Schritt 2: Benutzereingabe
user_input = input("💬 Was soll ich für dich speichern?\n> ")

# Schritt 3: Nachricht an den Thread anhängen
openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_input
)

# Schritt 4: Run starten
run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID
)

# Schritt 5: Warten, bis GPT fertig ist
print("⏳ GPT denkt nach...")
while True:
    run_status = openai.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(f"🔄 Status: {run_status.status}")

    
    if run_status.status == "requires_action":
        # GPT möchte eine Funktion aufrufen
        required_action = run_status.required_action

        tool_calls = required_action.submit_tool_outputs.tool_calls
        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\n🛠️ GPT fordert auf, {name}() aufzurufen mit:")
            print(json.dumps(arguments, indent=2))

            # Reminder als echtes Objekt speichern
            reminder = {
                "text": arguments["reminder_text"],
                "time": arguments["reminder_time"]
            }

            # Bestehende Daten laden (wenn vorhanden)
            try:
                with open("reminders.json", "r") as f:
                    reminders = json.load(f)
            except FileNotFoundError:
                reminders = []

            # Neuen Reminder anhängen
            reminders.append(reminder)

            # Datei speichern
            with open("reminders.json", "w") as f:
                json.dump(reminders, f, indent=2)

            print("✅ Erinnerung gespeichert in reminders.json")


            # Jetzt müssen wir GPT mitteilen, dass wir fertig sind:
            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": tool_call.id,
                        "output": "Erinnerung gespeichert!"
                    }
                ]
            )


# Schritt 6: Letzte Antwort abrufen
messages = openai.beta.threads.messages.list(thread_id=thread.id)
latest = messages.data[0]

# Schritt 7: Prüfen, ob GPT eine Funktion aufrufen will
content = latest.content[0]
if content.type == "text":
    print("💡 Antwort:", content.text.value)
elif content.type == "tool_calls":
    call = content.tool_calls[0]
    name = call.function.name
    args = json.loads(call.function.arguments)

    print(f"\n🛠️ GPT möchte {name}() aufrufen mit:")
    print(json.dumps(args, indent=2))

    # Hier kannst du später z. B. in eine Datenbank speichern
    print("\n✅ Funktionserkennung erfolgreich! (Speichern folgt im nächsten Schritt.)")
else:
    print("⚠️ Keine Antwort erkannt.")
