import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

assistant = openai.beta.assistants.create(
    name="SmartReminderGPT",
    instructions=(
        "Du bist ein persönlicher Assistent, der Erinnerungen für den Nutzer speichert "
        "und später auf Anfrage wiederfindet. Verwende den Vector Store über das file_search-Tool, "
        "um frühere Erinnerungen zu finden und anzuzeigen."
    ),
    model="gpt-4o",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": ["vs_68404a3fba4c8191abd0be2dd656b8fc"]
        }
    }
)

print("✅ Assistant erstellt:")
print("Assistant-ID:", assistant.id)
