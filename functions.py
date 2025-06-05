import openai
import os
import io


def save_reminder(title: str, time: str) -> None:
    """Speichert eine Erinnerung im OpenAI Vector Store."""
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    if not vector_store_id:
        raise ValueError("VECTOR_STORE_ID environment variable not set")

    content = f"Reminder: {title}\nTime: {time}"
    file_buffer = io.BytesIO(content.encode("utf-8"))

    # Datei für den Assistant hochladen
    openai.files.create(file=("reminder.txt", file_buffer), purpose="assistants")

    # Datei im Vector Store ablegen
    openai.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id,
        files=[("reminder.txt", io.BytesIO(content.encode("utf-8")))]
    )
