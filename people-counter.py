import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="centered")

# --- 1. NAČTENÍ SEZNAMU (Musí být na začátku, aby o něm Python věděl) ---
@st.cache_data(ttl=60)  # Kešuje seznam na 1 minutu
def nacti_scitace():
    default_list = ["– (Vyber jméno)", "Sčítač 1", "Sčítač 2"]
    try:
        with open("scitaci.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else default_list
    except Exception:
        return default_list

seznam_scitacu = nacti_scitace()

# --- INICIALIZACE STAVŮ (A RESET LOGIKY) ---
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None

def reset_formulkare():
    st.session_state.mod_dopravy_key = "Chodec 🚶"
    st.session_state.ve_skupine_key = False
    st.session_state.ma_psa_key = "–"
    st.session_state.ma_nakup_key = "–"
    st.session_state.ma_aktovku_key = "–"
    st.session_state.je_otocka_key = "–"
    st.session_state.vek_key = "– (Nezadáno)"
    st.session_state.poznamka_key = ""

if "mod_dopravy_key" not in st.session_state:
    reset_formulkare()

# --- ROZHRANÍ APLIKACE (MAXIMÁLNĚ KOMPAKTNÍ) ---

# Mód pohybu
mod_dopravy = st.radio(
    "Mód pohybu", 
    ["Chodec 🚶", "Běžec <b>🏃</b>", "Kolo 🚴", "Koloběžka 🛴", "Jiné"], 
    horizontal=True, 
    key="mod_dopravy_key",
    label_visibility="collapsed"
)

# Skupina
ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", key="ve_skupine_key")

# Třífázové parametry
c1, c2, c3 = st.columns(3)
with c1:
    ma_psa = st.radio("Pes? 🐕", ["–", "Ano", "Ne"], horizontal=True, key="ma_psa_key")
with c2:
    ma_nakup = st.radio("Nákup? 🛍️", ["–", "Ano", "Ne"], horizontal=True, key="ma_nakup_key")
with c3:
    ma_aktovku = st.radio("Školní aktovka? 🎒", ["–", "Ano", "Ne"], horizontal=True, key="ma_aktovku_key")

col_extra1, col_extra2 = st.columns(2)
with col_extra1:
    je_otocka = st.radio("Otočka/Návrat? 🔄", ["–", "Ano", "Ne"], horizontal=True, key="je_otocka_key")
with col_extra2:
    vek = st.selectbox("Věk", ["– (Nezadáno)", "Produktivní", "Dítě", "Teenager", "Senior"], key="vek_key", label_visibility="collapsed")

# Poznámka
poznamka = st.text_input("Poznámka", placeholder="Dobrovolná poznámka...", key="poznamka_key", label_visibility="collapsed")

# --- VÝBĚR SČÍTAČE (Nyní bezpečně dole nad tlačítky) ---
st.write("")
scitac = st.selectbox("Jméno sčítače", seznam_scitacu)

# --- LOGIKA ZÁPISU ---
def zapis_zaznam(smer):
    if scitac == "– (Vyber jméno)":
        st.error
