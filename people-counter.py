import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="centered")

# --- NAČTENÍ SEZNAMU JMÉNA Z GITHUB / LOKÁLNÊ ---
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

# 1. Výběr sčítače
scitac = st.selectbox("0", seznam_scitacu)
st.write("")

# Mód pohybu - popisek je skrytý, nezabírá místo
mod_dopravy = st.radio(
    "Mód pohybu", 
    ["Chodec 🚶", "Běžec 🏃", "Kolo 🚴", "Koloběžka 🛴", "Jiné"], 
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
    # Opravený selectbox s popiskem schovaným uvnitř možností tak, jak jsi to chtěl
    vek = st.selectbox("Věk", ["– (Nezadáno)", "Produktivní", "Dítě", "Teenager", "Senior"], key="vek_key", label_visibility="collapsed")

# Poznámka - popisek skrytý, viditelný je jen placeholder uvnitř pole
poznamka = st.text_input("Poznámka", placeholder="Dobrovolná poznámka...", key="poznamka_key", label_visibility="collapsed")

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
    
    reset_formulkare()

# --- AKČNÍ TLAČÍTKA ---
st.write("") 
col_prichod, col_odchod = st.columns(2)

with col_prichod:
    if st.button("📥 PŘÍCHOD", use_container_width=True, type="primary"):
        zapis_zaznam("prichod")
        st.rerun()

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
