from flask import flash
from huggingface_hub import InferenceClient
import os

LLM_PROVIDER = "together"


def get_huggingface_client():
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("ERROR: HUGGINGFACE_API_KEY environment variable not set.")
        flash("AI service is not configured correctly (Missing API Key).", "danger")
        return None
    try:
        client = InferenceClient(
            provider=LLM_PROVIDER,
            api_key=api_key,
        )
        return client
    except Exception as e:
        print(f"ERROR: Failed to create InferenceClient: {e}")
        flash(f"AI service connection error: {e}", "danger")
        return None