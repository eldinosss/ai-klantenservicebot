
import streamlit as st
from openai import OpenAI
import re
import json
import os

# --- SETTINGS ---
client = OpenAI(api_key="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")  # <-- Vul hier je echte OpenAI API-key in

st.set_page_config(page_title="AI Klantenservice Bot", layout="centered")
st.title("🤖 AI Klantenservice Bot – Meerdere Webshops")

# --- FAKE ORDER DATABASE ---
order_db = {
    "12345": "Je bestelling met ordernummer 12345 is onderweg en wordt bezorgd op 6 mei.",
    "98765": "Je bestelling met ordernummer 98765 is vandaag geleverd.",
    "55555": "Je bestelling met ordernummer 55555 is nog in behandeling en wordt morgen verzonden."
}

# --- LAAD FAQ-BESTANDEN UIT MAP ---
FAQ_MAP = "faqs"
faq_data = {}

if not os.path.exists(FAQ_MAP):
    os.makedirs(FAQ_MAP)

faq_files = [f for f in os.listdir(FAQ_MAP) if f.endswith(".json")]

# --- SELECTEER EEN SHOP FAQ ---
gekozen_shop = st.selectbox("📁 Kies een webshop FAQ-bestand", faq_files)

if gekozen_shop:
    with open(os.path.join(FAQ_MAP, gekozen_shop), "r", encoding="utf-8") as f:
        faq_data = json.load(f)
    st.success(f"FAQ geladen voor: {gekozen_shop}")

# --- SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- FUNCTIE OM ORDERNUMMER TE HERKENNEN ---
def check_order_status(vraag):
    match = re.search(r"(?:ordernummer|ordernr|#)(\d{5})", vraag)
    if match:
        nummer = match.group(1)
        if nummer in order_db:
            return order_db[nummer]
        else:
            return f"Ik heb geen bestelling gevonden met ordernummer {nummer}. Controleer het nummer en probeer het opnieuw."
    return None

# --- FUNCTIE OM FAQ TE DOORZOEKEN ---
def check_faq(vraag):
    for vraag_faq, antwoord_faq in faq_data.items():
        if vraag_faq.lower() in vraag.lower():
            return antwoord_faq
    return None

# --- GPT BACKUP ---
def antwoord_van_bot(vraag):
    order_antwoord = check_order_status(vraag)
    if order_antwoord:
        return order_antwoord

    faq_antwoord = check_faq(vraag)
    if faq_antwoord:
        return faq_antwoord

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een behulpzame klantenservicebot."},
                {"role": "user", "content": f"Antwoord kort, vriendelijk en duidelijk op deze klantvraag: {vraag}"}
            ]
        )
        antwoord = response.choices[0].message.content.strip()
        return antwoord
    except Exception as e:
        return f"Er is een fout opgetreden: {e}"

# --- CHAT INTERFACE ---
vraag = st.text_input("Typ je vraag hieronder:")

if vraag:
    st.session_state.chat_history.append(("👤", vraag))
    antwoord = antwoord_van_bot(vraag)
    st.session_state.chat_history.append(("🤖", antwoord))

# --- GESCHIEDENIS TONEN ---
for afzender, tekst in st.session_state.chat_history:
    st.markdown(f"**{afzender}**: {tekst}")
