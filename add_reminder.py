import openai
import io
import os

# 1. API-Key laden (über Replit Secret)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2. Inhalt für die Erinnerung (Text + Zeit)
file_content = "Reminder: Lisa schreiben\nTime: 2025-06-11T09:00:00"
file_buffer = io.BytesIO(file_content.encode("utf-8"))

# 3. Datei hochladen (erzeugt ein FileObject, aber wir brauchen das FileObject hier
#    nur zur Info; tatsächlich übergeben wir später den reinen Tupel-Parameter erneut)
created_file = openai.files.create(
    file=("reminder.txt", file_buffer),
    purpose="assistants"
)

print("✅ Datei erfolgreich hochgeladen (File-ID):", created_file.id)

# 4. ***WICHTIG***: dieselbe Datei als Tupel nochmal an upload_and_poll übergeben
#    Damit sagt ihr OpenAI: 'Speichere diese Datei jetzt im Vector Store ab.'
vector_store_id = "vs_68404a3fba4c8191abd0be2dd656b8fc"

# ACHTUNG: Hier nicht `files=[created_file]` und nicht `files=[created_file.id]`, 
# sondern **wieder genau dieselbe Tupel-Notation**:
openai.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store_id,
    files=[("reminder.txt", io.BytesIO(file_content.encode("utf-8")))]
)

print("✅ Datei im Vector Store gespeichert.")
