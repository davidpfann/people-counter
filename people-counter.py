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

# --- INICIALIZACE STAVŮ ---
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None

# Výchozí hodnoty pro čistý start
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
    st.session_state.vek_key = "– (Nezadáno)"
if "poznamka_key" not in st.session_state:
    st.session_state.poznamka_key = ""

# --- ROZHRANÍ APLIKACE ---

# Mód pohybu
mod_dopravy = st.radio(
    "Mód pohybu", 
    ["Chodec 🚶", "Běžec 🏃", "Kolo 🚴", "Koloběžka 🛴", "Jiné"], 
    horizontal=True, 
    key="mod_dopravy_key",
    label_visibility="collapsed"
)

# Skupina
ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", key="ve_skupine_key")

# --- PARAMETRY NA JEDEN ŘÁDEK (Fixní rozvržení pro mobily) ---
# Používáme flexibilní CSS grid, který se na mobilu nikdy nerozpadne na dva řádky
st.markdown("""
<style>
.row-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: -10px;
}
.label-text {
    font-weight: bold;
    font-size: 16px;
    white-space: nowrap;
}
</style>
""", unsafe_html=True)

# 1. Pes
st.markdown("<div class='row-container'><div class='label-text'>Pes? 🐕</div></div>", unsafe_html=True)
ma_psa = st.radio("Pes", ["–", "Ano", "Ne"], horizontal=True, key="ma_psa_key", label_visibility="collapsed")

# 2. Nákup
st.markdown("<div class='row-container'><div class='label-text'>Nákup? 🛍️</div></div>", unsafe_html=True)
ma_nakup = st.radio("Nákup", ["–", "Ano", "Ne"], horizontal=True, key="ma_nakup_key", label_visibility="collapsed")

# 3. Aktovka
st.markdown("<div class='row-container'><div class='label-text'>Aktovka? 🎒</div></div>", unsafe_html=True)
ma_aktovku = st.radio("Aktovka", ["–", "Ano", "Ne"], horizontal=True, key="ma_aktovku_key", label_visibility="collapsed")

# 4. Otočka
st.markdown("<div class='row-container'><div class='label-text'>Otočka? 🔄</div></div>", unsafe_html=True)
je_otocka = st.radio("Otočka", ["–", "Ano", "Ne"], horizontal=True, key="je_otocka_key", label_visibility="collapsed")

# Věk a Poznámka vedle sebe
st.write("")
col_v, col_p = st.columns(2)
with col_v:
    vek = st.selectbox("Věk", ["– (Nezadáno)", "Produktivní", "Dítě", "Teenager", "Senior"], key="vek_key", label_visibility="collapsed")
with col_p:
    poznamka = st.text_input("Poznámka", placeholder="Dobrovolná poznámka...", key="poznamka_key", label_visibility="collapsed")

# --- VÝBĚR SČÍTAČE ---
st.write("")
scitac = st.selectbox("Jméno sčítače", seznam_scitacu)

# --- FUNKCE PRO ZÁPIS A RESET (Opravený název) ---
def zpracuj_kliknuti(smer):
    if scitac == "– (Vyber jméno)":
        st.session_state["chyba_scitace"] = True
        return
    else:
        st.session_state["chyba_scitace"] = False

    nyni = datetime.datetime.now()
    timestamp_str = nyni.strftime("%Y-%m-%d %H:%M:%S")
    
    def preved_stav(hodnota):
        if hodnota == "Ano": return True
        if hodnota == "Ne": return False
        return None

    je_skupina = False
    id_skupiny = None

    v_ve_skupine = st.session_state.ve_skupine_key
    v_mod_dopravy = st.session_state.mod_dopravy_key
    v_vek = st.session_state.vek_key
    v_ma_psa = st.session_state.ma_psa_key
    v_ma_nakup = st.session_state.ma_nakup_key
    v_ma_aktovku = st.session_state.ma_aktovku_key
    v_je_otocka = st.session_state.je_otocka_key
    v_poznamka = st.session_state.poznamka_key

    if v_ve_skupine:
        je_skupina = True
        if st.session_state.aktualni_id_skupiny is not None:
            id_skupiny = st.session_state.aktualni_id_skupiny
        else:
            if st.session_state.scitani_data:
                posledni_index = len(st.session_state.scitani_data) - 1
