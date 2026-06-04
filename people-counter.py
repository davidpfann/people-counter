import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="centered")

# --- 1. NAČTENÍ SEZNAMU ---
@st.cache_data(ttl=60)
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

# --- ROZHRANÍ APLIKACE ---

# Mód pohybu (Opraven překlep s HTML tagem)
mod_dopravy = st.radio(
    "Mód pohybu", 
    ["Chodec 🚶", "Běžec 🏃", "Kolo 🚴", "Koloběžka 🛴", "Jiné"], 
    horizontal=True, 
    key="mod_dopravy_key",
    label_visibility="collapsed"
)

# Skupina
ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", key="ve_skupine_key")

# --- PARAMETRY NA JEDEN ŘÁDEK ---
# Použijeme sloupce, kde vlevo je text a vpravo tlačítka, vertikálně zarovnaná

# 1. Pes
r1_col1, r1_col2 = st.columns([1, 2])
with r1_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Pes? 🐕</b></div>", unsafe_html=True)
with r1_col2:
    ma_psa = st.radio("Pes", ["–", "Ano", "Ne"], horizontal=True, key="ma_psa_key", label_visibility="collapsed")

# 2. Nákup
r2_col1, r2_col2 = st.columns([1, 2])
with r2_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Nákup? 🛍️</b></div>", unsafe_html=True)
with r2_col2:
    ma_nakup = st.radio("Nákup", ["–", "Ano", "Ne"], horizontal=True, key="ma_nakup_key", label_visibility="collapsed")

# 3. Aktovka
r3_col1, r3_col2 = st.columns([1, 2])
with r3_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Aktovka? 🎒</b></div>", unsafe_html=True)
with r3_col2:
    ma_aktovku = st.radio("Aktovka", ["–", "Ano", "Ne"], horizontal=True, key="ma_aktovku_
