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

# Výchozí hodnoty pro reset (Toggley začínají jako False)
if "mod_dopravy_key" not in st.session_state:
    st.session_state.mod_dopravy_key = "Chodec 🚶"
if "ve_skupine_key" not in st.session_state:
    st.session_state.ve_skupine_key = False
if "ma_psa_key" not in st.session_state:
    st.session_state.ma_psa_key = False
if "ma_nakup_key" not in st.session_state:
    st.session_state.ma_nakup_key = False
if "ma_aktovku_key" not in st.session_state:
    st.session_state.ma_aktovku_key = False
if "je_otocka_key" not in st.session_state:
    st.session_state.je_otocka_key = False
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

# --- JEDNOŘÁDKOVÉ PARAMETRY POMOCÍ NATÍVNÍCH TOGGLES ---
ma_psa = st.toggle("🐕 Pes?", key="ma_psa_key")
ma_nakup = st.toggle("🛍️ Nákup?", key="ma_nakup_key")
ma_aktovku = st.toggle("🎒 Školní aktovka?", key="ma_aktovku_key")
je_otocka = st.toggle("🔄 Otočka/Návrat?", key="je_otocka_key")

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

# --- FUNKCE PRO ZÁPIS A RESET ---
def zpracuj_kliknuti(smer):
    if scitac == "– (Vyber jméno)":
        st.session_state["chyba_scitace"] = True
        return
    else:
        st.session_state["chyba_scitace"] = False

    nyni = datetime.datetime.now()
    timestamp_str = nyni.strftime("%Y-%m-%d %H:%M:%S")

    je_skupina = False
    id_skupiny = None

    # Načtení hodnot z session_state přes klíče
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
                id_skupiny = st.session_state.scitani_data[posledni_index]["Timestamp"].replace(" ", "_")
                st.session_state.scitani_data[posledni_index]["Je_skupina"] = True
                st.session_state.scitani_data[posledni_index]["ID_skupiny"] = id_skupiny
                st.session_state.aktualni_id_skupiny = id_skupiny
            else:
                id_skupiny = timestamp_str.replace(" ", "_")
                st.session_state.aktualni_id_skupiny = id_skupiny
    else:
        st.session_state.aktualni_id_skupiny = None

    # Pokud je zapnutý toggle, zapíše se True. Pokud je vypnutý, zapíše se None (Nezadáno/Prázdné políčko)
    zaznam = {
        "Timestamp": timestamp_str,
        "Scitac": scitac,
        "Smer": smer,
        "Mod_pohybu": v_mod_dopravy,
        "Vek": v_vek if v_vek != "– (Nezadáno)" else None,
        "Pes": True if v_ma_psa else None,
        "Nakup": True if v_ma_nakup else None,
        "Aktovka": True if v_ma_aktovku else None,
        "Otocka": True if v_je_otocka else None,
        "Je_skupina": je_skupina,
        "ID_skupiny": id_skupiny,
        "Poznamka": v_poznamka if v_poznamka else None
    }
    
    st.session_state.scitani_data.append(zaznam)
    
    # Automatický reset po uložení
    st.session_state.mod_dopravy_key = "Chodec 🚶"
    st.session_state.ve_skupine_key = False
    st.session_state.ma_psa_key = False
    st.session_state.ma_nakup_key = False
    st.session_state.ma_aktovku_key = False
    st.session_state.je_otocka_key = False
    st.session_state.vek_key = "– (Nezadáno)"
    st.session_state.poznamka_key = ""

# Zobrazení chybové hlášky
if st.session_state.get("chyba_scitace", False):
    st.error("❌ Před zaznamenáním průchodu musíte dole vybrat své JMÉNO!")

# --- AKČNÍ TLAČÍTKA ---
st.write("") 
col_prichod, col_odchod = st.columns(2)

with col_prichod:
    st.button("📥 PŘÍCHOD", use_container_width=True, type="primary", on_click=zpracuj_kliknuti, args=("prichod",))

with col_odchod:
    st.button("📤 ODCHOD", use_container_width=True, type="primary", on_click=zpracuj_kliknuti, args=("odchod",))

# --- EXPORT VÝSLEDKŮ ---
if st.session_state.scitani_data:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(3), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Stáhnout kompletní CSV", csv, "scitani_chodcu.csv", "text/csv", use_container_width=True)
