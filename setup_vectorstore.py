import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Schritt 1: Vector Store erstellen
vector_store = openai.vector_stores.create(
    name="ReminderMemory",
)


print("✅ Vector Store erstellt:", vector_store.id)
