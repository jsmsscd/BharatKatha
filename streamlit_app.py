# streamlit_app.py
# Smart Cultural Storyteller — BharatKatha Streamlit Frontend
# By Paarthi Sharma

import streamlit as st
import requests
import json

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
API_URL = "http://127.0.0.1:5002/generate"

st.set_page_config(
    page_title="Bharat Katha — Smart Cultural Storyteller",
    page_icon="🎙️",
    layout="centered",
)

# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------
st.title("🎙️ Bharat Katha — Smart Cultural Storyteller")
st.markdown(
    """
    *Experience Indian history, folk tales, and traditions through an AI-powered storyteller.*
    Choose an era and emotion (Rasa), and let BharatKatha narrate a tale of heritage.
    """
)

# ------------------------------------------------------------
# USER INPUTS
# ------------------------------------------------------------
eras = ["Indus", "Mauryan", "Sangam" , "Gupta", "Medieval", "Colonial", "Mughal", "Maratha", "Modern"]
rasas = ["Karuna (Compassion)", "Veer (Courage)", "Adbhuta (Wonder)", "Bhakti (Devotion)", "Hasya (Joy) ","Shanta (peace) ","Raudra (fury)", "Vira (Heroism)"]

era = st.selectbox("🕰️ Choose an Era:", eras, index=0)
rasa = st.selectbox("💫 Choose a Rasa:", rasas, index=0)

tts = st.checkbox("🎧 Generate Audio", value=True)
image = st.checkbox("🖼️ Generate Image", value=True)

# Extract rasa key from label
rasa_key = rasa.split(" ")[0].strip().lower()

# ------------------------------------------------------------
# SUBMIT BUTTON
# ------------------------------------------------------------
if st.button("✨ Tell Me a Story"):
    st.info("Generating your story... please wait a moment ⏳")

    payload = {"era": era, "rasa": rasa_key, "tts": tts, "image": image}

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code != 200:
            st.error(f"Error: {response.status_code}\n{response.text}")
        else:
            data = response.json()
            story = data.get("story", {})

            # ------------------------------------------------------------
            # DISPLAY STORY
            # ------------------------------------------------------------
            st.subheader(story.get("title", "Untitled Story"))
            st.caption(f"Era: {story.get('era_title')} | Rasa: {story.get('rasa_label')}")
            st.write(story.get("text", "No story generated."))
            st.markdown(f"**Moral:** {story.get('moral', '—')}")

            # ------------------------------------------------------------
            # AUDIO
            # ------------------------------------------------------------
            if tts and data.get("audio_url"):
                audio_url = f"http://127.0.0.1:5002{data['audio_url']}"
                st.audio(audio_url, format="audio/wav")

            # ------------------------------------------------------------
            # IMAGE
            # ------------------------------------------------------------
            if image and data.get("image_url"):
                img_url = f"http://127.0.0.1:5002{data['image_url']}"
                st.image(img_url, caption="Story Illustration")

            # ------------------------------------------------------------
            # SAVE STORY JSON
            # ------------------------------------------------------------
            story_json = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button(
                "💾 Download Story JSON",
                story_json,
                file_name=f"story_{story.get('id', 'unknown')}.json",
                mime="application/json",
            )

    except requests.exceptions.ConnectionError:
        st.error("🚫 Could not connect to BharatKatha API. Please ensure it’s running.")
