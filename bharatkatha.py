# bharatkatha.py
# Smart Cultural Storyteller – Bharat Katha API
# Version: UTF-8 Safe + TTS + Image Support

import os
import json
import random
import string
import argparse
import sys
from flask import Flask, request, jsonify

# Optional libraries
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None

# ---------------------------------------------------------------------
# GLOBAL SETTINGS
# ---------------------------------------------------------------------
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
AUDIO_DIR = "static/audio"
IMAGE_DIR = "static/images"
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------
def slug(length=6):
    """Generate random short ID."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def clean_text(s: str) -> str:
    """Remove or replace fancy punctuation for TTS compatibility."""
    return (
        s.replace("—", "-")
         .replace("–", "-")
         .replace("‘", "'")
         .replace("’", "'")
         .replace("“", '"')
         .replace("”", '"')
         .replace("…", "...")
    )


# ---------------------------------------------------------------------
# STORY GENERATOR (SIMPLE DEMO)
# ---------------------------------------------------------------------
ERAS = {
    "indus": "Sindhu-Sarasvati (Indus)",
    "mauryan": "Mauryan Era",
    "sangam": "Sangam Age",
    "gupta": "Gupta Golden Age",
    "medieval": "Bhakti & Sufi",
    "colonial": "Colonial & Freedom",
    "mughal": "Mughal Era",
    "maratha": "Maratha Confederacy",
    "modern": "Modern India"
}
RASAS = {
    "karuna": "Compassion",
    "veer": "Courage",
    "adbhuta": "Wonder",
    "bhakti": "Devotion",
    "hasya": "Joy",
    "shanta": "Peace",
    "raudra": "Fury",
    "vira": "Heroism"
}
STORY_TEMPLATES = { "indus": {
        "adbhuta": [
           " Long before time learned to count its years, in the city of Dholavira, the earth itself seemed alive. Streets ran straight as thought, and houses breathed in rhythm with the wind. But the true marvel of the city lay hidden beneath — a maze of wells and channels that sang softly when water flowed through them.A young girl named Mira, the daughter of an engineer, often wandered near these wells.She believed they spoke — murmuring secrets from the river Sarasvati far beyond sight.Her father laughed, saying, “They whisper only to those who listen with patience.”One summer, when the rains failed and the reservoirs dried, panic gripped the people.Crops wilted, and the wells stood silent. But Mira remembered the tones she had once heard — the rhythm of water echoing deep below. Guided by sound alone, she found an untouched underground stream.The city rejoiced. Engineers followed her steps, mapping the secret aquifer, and Dholavira thrived again. From then on, the wells were no longer mere constructions of stone — they were living wonders, voices of the earth that had spoken through a child’s faith."
        ],
        "veer": [
            "In the prosperous city of Harappa, where merchants thrived and craftsmen shaped beauty out of stone and bronze, there stood the Great Bath — a place where purity met the spirit of the people.It was said that the strength of the city flowed from its waters, binding community and faith together.One night, when the moon hung low and the wind carried whispers of unrest, a sudden tremor shook the earth.A section of the city wall cracked, and water from the sacred bath began to rush toward the sleeping quarters. Panic spread through the streets as people fled their homes.But Arav, a young mason’s apprentice, refused to run. He had helped build the very walls that now trembled. Without waiting for command or reward, he gathered clay bricks and wooden beams, and alone in the darkness, began to rebuild the breach.His hands bled, his breath faltered, yet he worked until dawn.When morning came, the flood had been contained. The elders declared that the gods themselves had guided his hands, but Arav only smiled and said, “It was not the gods, but the duty of a son to guard his city.From that day, the tale of the Guardian of the Great Bath became a hymn of courage whispered across the Indus plains — a reminder that even in silence, valor can echo for centuries."
        ],
        "karuna": [
            "In the heart of the ancient city of Mohenjo-Daro, where brick houses lined the streets and the sound of trade echoed through the bazaars, lived a humble potter named Ravi. His hands shaped clay from the Indus River into vessels that carried water, grain, and dreams.One summer, a terrible drought struck the land. Wells dried, and the once-mighty Indus shrank into a quiet stream. The wealthy traders hoarded water in hidden tanks, while the poor wandered the alleys, parched and desperate.One evening, Ravi found a child fainting near his kiln — the potter’s wheel still turning as if whispering fate. Without a second thought, he poured his last pot of water into the child’s cupped hands. His wife wept — for that was all they had left — but Ravi said gently, “What use is clay if the soul it serves is empty?The next morning, rain clouds gathered over the horizon.It was said that the heavens, moved by the compassion of one potter, wept upon the thirsty earth. The city rejoiced, and from that day, the people of Mohenjo-Daro remembered that compassion is the purest form of creation."
        ],
    },
    "mauryan": {
        "karuna": [
            "A royal edict taught that even kings must bow to the measure of suffering.",
            "A monk rode the dusty road and convinced a soldier to spare a village's herd."
        ],
        "adbhuta": [
            "On a pillar, the script glowed like a constellation, mapping law and care."
        ],
    },
    "sangam": {
        "adbhuta": [
            "Poems stitched across the harbour, and each verse was a knot binding distant coasts."
        ],
        "hasya": [
            "A fisher's joke saved a poet's day and the poem kept laughing across generations."
        ],
    },
    "gupta": {
        "adbhuta": [
            "A scholar charted the stars and learned that numbers could hold songs."
        ],
        "veer": [
            "Temples echoed with debates where courage took the form of new ideas."
        ],
    },
    "medieval": {
        "bhakti": [
            "A saint sang at dawn. People came not for doctrine but for the warmth in his voice."
        ],
        "karuna": [
            "A traveler found shelter in a stranger's courtyard, and it began a chain of kindness."
        ],
    },
    "colonial": {
        "veer": [
            "Pamphlets were folded like small boats; words carried people to new shores."
        ],
        "karuna": [
            "Reformers argued that law must protect the weakest; the streets listened."
        ],
    },
}
    
def generate_story(era: str, rasa: str):
    """Generate a story dynamically using multiple templates."""
    era_key = era.lower()
    rasa_key = rasa.lower()
    
    # Fallback title and rasa
    title = ERAS.get(era_key, "A Forgotten Era")
    rasa_label = RASAS.get(rasa_key, rasa.capitalize())
    
    # Choose template randomly
    templates = STORY_TEMPLATES.get(era_key, {}).get(rasa_key, [])
    if templates:
        story_text = random.choice(templates)
    else:
        story_text = (
            f"In the {era.capitalize()} period, tales of {rasa_label.lower()} "
            f"inspired hearts and guided communities."
        )
    
    moral_lines = {
        "karuna": "The strength of a civilization lies in its empathy.",
        "veer": "Courage shapes the destiny of many.",
        "adbhuta": "Wonder keeps wisdom alive.",
        "bhakti": "Devotion transforms ordinary into sacred.",
        "hasya": "Joy preserves memories across generations.",
        "shanta": "Peace binds hearts and minds.",
        "raudra": "Fury warns and protects.",
        "vira": "Heroism endures through deeds."
    }
    
    moral = moral_lines.get(rasa_key, "Every story carries a lesson.")

    return {
        "id": slug(),
        "title": title,
        "era_title": era.capitalize(),
        "rasa_label": rasa_label,
        "text": story_text,
        "moral": moral
    }


# ---------------------------------------------------------------------
# TTS (TEXT TO SPEECH)
# ---------------------------------------------------------------------
def synthesize_speech(text, filename):
    """Convert story text to speech and save."""
    if not pyttsx3:
        raise ImportError("pyttsx3 not installed. Run: pip install pyttsx3")

    engine = pyttsx3.init()
    safe_text = clean_text(text)

    # Adjust speech properties
    engine.setProperty("rate", 150)
    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)

    # Save as WAV (most reliable format)
    engine.save_to_file(safe_text, filename)
    engine.runAndWait()

    return filename

# ---------------------------------------------------------------------
# IMAGE GENERATOR (PLACEHOLDER)
# ---------------------------------------------------------------------
def generate_image(text, filename):
    """Generate a simple image with PIL for the story title."""
    if not Image:
        raise ImportError("Pillow not installed. Run: pip install pillow")

    img = Image.new("RGB", (600, 400), color=(250, 240, 220))
    d = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()

    d.text((30,70), clean_text(text[:60]), fill=(80, 40, 20), font=font)
    img.save(filename)
    return filename

# ---------------------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------------------
@app.route("/generate", methods=["POST"])
def generate():
    """Main route to generate story + optional audio/image."""
    try:
        data = request.get_json(force=True)
        era = data.get("era", "mauryan")
        rasa = data.get("rasa", "karuna")
        make_tts = data.get("tts", False)
        make_image = data.get("image", False)

        story = generate_story(era, rasa)
        result = {"story": story}

        # Optional: Audio
        if make_tts:
            audio_path = os.path.join(AUDIO_DIR, f"speech_{slug()}.wav")
            synthesize_speech(story["text"], audio_path)
            result["audio_url"] = "/" + audio_path.replace("\\", "/")

        # Optional: Image
        if make_image:
            image_path = os.path.join(IMAGE_DIR, f"img_{slug()}.png")
            generate_image(story["title"], image_path)
            result["image_url"] = "/" + image_path.replace("\\", "/")

        # UTF-8 safe JSON response
        return app.response_class(
            response=json.dumps(result, ensure_ascii=False, indent=2),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        return app.response_class(
            response=json.dumps({"error": str(e)}, ensure_ascii=False),
            status=500,
            mimetype="application/json"
        )

# ---------------------------------------------------------------------
# TEST ROUTE (for Unicode check)
# ---------------------------------------------------------------------
@app.route("/test")
def test_unicode():
    return app.response_class(
        response=json.dumps({"msg": "Hello — नमस्ते — வணக்கம்"}, ensure_ascii=False),
        status=200,
        mimetype="application/json"
    )

# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="Run as Flask API server")
    args = parser.parse_args()

    if args.serve:
        print("[Server] Starting BharatKatha API on http://127.0.0.1:5002")
        app.run(host="127.0.0.1", port=5002, debug=True)
    else:
        # Standalone test
        s = generate_story("mauryan", "karuna")
        print(json.dumps(s, ensure_ascii=False, indent=2))
