# client_test.py
# BharatKatha API Client
# Author: Paarthi Sharma’s Smart Cultural Storyteller project

import requests
import json

API_URL = "http://127.0.0.1:5002/generate"

def generate_story(era, rasa, tts=False, image=False, persona=None):
    """Send request to BharatKatha API and display result."""
    payload = {
        "era": era,
        "rasa": rasa,
        "tts": tts,
        "image": image,
        "persona": persona
    }

    print(f"\n[INFO] Requesting story for Era: {era}, Rasa: {rasa}")
    try:
        response = requests.post(API_URL, json=payload)
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to BharatKatha API. Is the server running?")
        return None

    if response.status_code != 200:
        print(f"[ERROR] {response.status_code}: {response.text}")
        return None

    data = response.json()
    story = data.get("story", {})

    # Display story info
    print("\n=== STORY GENERATED ===")
    print(f"Title: {story.get('title', 'Untitled')}")
    print(f"Era: {story.get('era_title', 'Unknown')} | Rasa: {story.get('rasa_label', 'Unknown')}\n")

    print("Text:\n" + story.get("text", "No story text found.") + "\n")
    print("Moral:", story.get("moral", "—"))

    # Audio + Image URLs (if generated)
    if data.get("audio_url"):
        print("\n🎧 Audio available at:", f"http://127.0.0.1:5002{data['audio_url']}")
    if data.get("image_url"):
        print("🖼️ Image available at:", f"http://127.0.0.1:5002{data['image_url']}")

    # Save output locally
    file_name = f"story_{story.get('id', 'unknown')}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] Story saved as {file_name}")

    return data


if __name__ == "__main__":
    # Example 1 — Text only
    generate_story("mauryan", "karuna")

    # Example 2 — Text + Audio + Image
    generate_story("gupta", "adbhuta", tts=True, image=True)

    # Example 3 — Another variation
    # generate_story("medieval", "bhakti", tts=True)
