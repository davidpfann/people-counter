import streamlit as st
import datetime
import pandas as pd
import json

st.set_page_config(layout="centered")

# --- 1. NAČTENÍ SEZNAMU SČÍTAČŮ ---
@st.cache_data(ttl=60)
def nacti_scitace():
    default_list = ["– (Vyber jméno sčítače)", "Sčítač 1", "Sčítač 2"]
    try:
        with open("scitaci.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else default_list
    except Exception:
        return default_list

seznam_scitacu = nacti_scitace()

# --- 2. LOGIKA PRO LOCAL STORAGE (PAMĚŤ TELEFONU) ---
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None

# Načtení z paměti prohlížeče při startu
if "prazdny_start" not in st.session_state:
    st.session_state.prazdny_start = True
    js_load = """
    <script>
    const data = localStorage.getItem('scitani_backup');
    if (data) {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*');
    } else {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: '[]'}, '*');
    }
    </script>
    """
    st.components.v1.html(js_load, height=0, width=0)

backup_data = st.session_state.get("backup_bridge")
if backup_data and st.session_state.prazdny_start:
    try:
        loaded_data = json.loads(backup_data)
        if loaded_data and not st.session_state.scitani_data:
            st.session_state.scitani_data = loaded_data
    except Exception:
        pass
    st.session_state.prazdny_start = False

# Výchozí hodnoty pro reset formuláře
if "mod_dopravy_key" not in st.session_state:
    st.session_state.mod_dopravy_key = "Chodec 🚶"
if "ve_skupine_key" not in st.session_state:
    st.session_state.ve_skupine_key = False
if "ma_psa_key" not in st.session_state:
    st.session_state.ma_psa_key = "–"
if "ma_nakup_key" not in st.session_state:
    st.session_state.ma_nakup_key = "–"
if "ma_aktovku_key" not in st.session_state:
    st.session_state.ma_aktovku_key = "–"
if "je_otocka_key" not in st.session_state:
    st.session_state.je_otocka_key = "–"
if "vek_key" not in st.session_state:
    st.session_state.vek_key = "Nezadán"
if "poznamka_key" not in st.session_state:
    st.session_state.poznamka_key = ""

# --- ROZHRANÍ APLIKACE ---

# Mód pohybu
mod_dopravy = st.segmented_control(
    "Mód pohybu",
    ["Chodec 🚶", "Běžec 🏃", "Kolo 🚴", "Koloběžka 🛴", "Jiné"],
    key="mod_dopravy_key",
    label_visibility="collapsed"
)

# --- PARAMETRY ROZDĚLENÉ DO ŘÁDKŮ (OPRAVENO: Unikátní klíče doplňují data) ---

# 1. Řádek: Pes
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🐶 Pes?")
with col2:
    ma_psa = st.segmented_control("Pes", ["–", "Ano", "Ne"], key="ma_psa_key", label_visibility="collapsed")

# 2. Řádek: Školní aktovka
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🎒 Školní aktovka?")
with col2:
    ma_aktovku = st.segmented_control("Aktovka", ["–", "Ano", "Ne"], key="ma_aktovku_key", label_visibility="collapsed")

# 3. Řádek: Nákup
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🛍️ Nákup?")
with col2:
    ma_nakup = st.segmented_control("Nákup", ["–", "Ano", "Ne"], key="ma_nakup_key", label_visibility="collapsed")

# 4. Řádek: Otočka/Návrat
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🔄 Otočka/Návrat?")
with col2:
    je_otocka = st.segmented_control
