import streamlit as st
import datetime
import pandas as pd
import requests

st.set_page_config(layout="centered")

# --- NAČTENÍ SEZNAMU JMÉNA Z GITHUB / LOKÁLNĚ ---
@st.cache_data(ttl=60)  # Kešuje seznam na 1 minutu, aby se nestahoval při každém kliku
def nacti_scitace():
    default_list = ["– (Vyber jméno)", "Sčítač 1", "Sčítač 2"]
    try:
        # Streamlit zkusí přečíst lokální soubor scitaci.txt v repozitáři
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

# Funkce, která vrátí všechny ovládací prvky do výchozího stavu
def reset_formulkare():
    st.session_state.mod_dopravy_key = "Chodec 🚶"
    st.session_state.ve_skupine_key = False
    st.session_state.ma_psa_key = "–"
    st.session_state.ma_nakup_key = "–"
    st.session_state.ma_aktovku_key = "–"
    st.session_state.je_otocka_key = "–"
    st.session_state.vek_key = "– (Nezadáno)"
    st.session_state.poznamka_key = ""

# Inicializace klíčů, pokud ještě neexistují
if "mod_dopravy_key" not in st.session_state:
    reset_formulkare()

# --- ROZHRANÍ APLIKACE (BEZ NADPISŮ) ---

# 1. Výběr sčítače na samém úvodu
scitac = st.selectbox("Jméno sčítače", seznam_scitacu)

# Vizuální oddělení, které nezabírá místo
st.write("")

# Mód pohybu (bez nadpisu, stačí popisek uvnitř)
mod_dopravy = st.radio("Mód pohybu", ["Chodec 🚶", "Běžec 🏃", "Na kole 🚴", "Koloběžka 🛴"], horizontal=True, key="mod_dopravy_key")

# Skupina
ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", key="ve_skupine_key")

# Parametry uspořádané: NEZADÁNO (–) - ANO - NE
c1, c2, c3 = st.columns(3)
with c1:
    ma_psa = st.radio("Pes? 🐕", ["–", "Ano", "Ne"], horizontal=True, key="ma_psa_key")
with c2:
    ma_nakup = st.radio("Nákup? 🛍️", ["–", "Ano", "Ne"], horizontal=True, key="ma_nakup_key")
with c3:
    ma_aktovku = st.radio("Aktovka? 🎒", ["–", "Ano", "Ne"], horizontal=True, key="ma_aktovku_key")

col_extra1, col_extra2 = st.columns(2)
with col_extra1:
    je_otocka = st.radio("Otočka/Návrat? 🔄", ["–", "Ano", "Ne"], horizontal=True, key="je_otocka_key")
with col_extra2:
    vek = st.selectbox("Věk", ["– (Nezadáno)", "Produktivní", "Dítě", "Teenager", "Senior"], key="vek_key")

poznamka = st.text_input("Obecná poznámka", placeholder="Dobrovolná poznámka...", key="poznamka_key")

# --- LOGIKA ZÁPISU ---
def zapis_zaznam(smer):
    if scitac == "– (Vyber jméno)":
        st.error("❌ Před zaznamenáním průchodu musíte vybrat své JMÉNO na začátku stránky!")
        return

    nyni = datetime.datetime.now()
    timestamp_str = nyni.strftime("%Y-%m-%d %H:%M:%S")
    
    def preved_stav(hodnota):
        if hodnota == "Ano": return True
        if hodnota == "Ne": return False
        return None

    je_skupina = False
    id_skupiny = None

    if ve_skupine:
        je_skupina = True
        if st.session_state.aktualni_id_skupiny is not None:
            id_skupiny = st.session_state.aktualni_id_skupiny
        else:
            if st.session_state.scitani_data:
                posledni_index = len(st.session_state.scitani_data) - 1
                id_skupiny = st.session_state.scitani_data[posledni_index]["Timestamp"].replace(" ", "_")
                st.session_state.scitani_data[posledni_index]["Je_skupina"] = True
                st.session_state.scitani_data[posledni_index]["ID_skupiny"] = id_skupiny
                st.session_state.aktualni_id_skupiny = id_skupiny
            else:
                id_skupiny = timestamp_str.replace(" ", "_")
                st.session_state.aktualni_id_skupiny = id_skupiny
    else:
        st.session_state.aktualni_id_skupiny = None

    zaznam = {
        "Timestamp": timestamp_str,
        "Scitac": scitac,
        "Smer": smer,
        "Mod_pohybu": mod_dopravy,
        "Vek": vek if vek != "– (Nezadáno)" else None,
        "Pes": preved_stav(ma_psa),
        "Nakup": preved_stav(ma_nakup),
        "Aktovka": preved_stav(ma_aktovku),
        "Otocka": preved_stav(je_otocka),
        "Je_skupina": je_skupina,
        "ID_skupiny": id_skupiny,
        "Poznamka": poznamka if poznamka else None
    }
    
    st.session_state.scitani_data.append(zaznam)
    st.toast(f"Zapsán {smer.upper()}: {mod_dopravy}", icon="✅")
    
    # Spuštění resetu formuláře pro další kliknutí
    reset_formulkare()

# --- AKČNÍ TLAČÍTKA ---
st.write("") # Drobné odskočení od formuláře místo tlusté čáry
col_prichod, col_odchod = st.columns(2)

with col_prichod:
    if st.button("📥 PŘÍCHOD", use_container_width=True, type="primary"):
        zapis_zaznam("prichod")
        st.rerun() # Okamžitě překreslí aplikaci s vyčištěnými hodnotami

with col_odchod:
    if st.button("📤 ODCHOD", use_container_width=True, type="primary"):
        zapis_zaznam("odchod")
        st.rerun()

# --- EXPORT VÝSLEDKŮ ---
if st.session_state.scitani_data:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(3), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Stáhnout kompletní CSV", csv, "scitani_chodcu.csv", "text/csv", use_container_width=True)
