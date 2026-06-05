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
    ["Chodec 🚶", "Běžec 🏃", "🚴", "🛴", "🛼", "Jiné"],
    key="mod_dopravy_key",
    label_visibility="collapsed"
)

# --- PARAMETRY (Zkrácené texty a menší písmo, aby držely řádek) ---

# 1. Řádek: Pes
col1, col2 = st.columns([4, 3])
with col1:
    st.write("**🐕 Pes?**")
with col2:
    ma_psa = st.segmented_control("Pes", ["–", "Ano", "Ne"], key="ma_psa_key", label_visibility="collapsed")

# 2. Řádek: Aktovka
col1, col2 = st.columns([4, 3])
with col1:
    st.write("**🎒 Aktovka?**")
with col2:
    ma_aktovku = st.segmented_control("Aktovka", ["–", "Ano", "Ne"], key="ma_aktovku_key", label_visibility="collapsed")

# 3. Řádek: Nákup
col1, col2 = st.columns([4, 3])
with col1:
    st.write("**🛍️ Nákup?**")
with col2:
    ma_nakup = st.segmented_control("Nákup", ["–", "Ano", "Ne"], key="ma_nakup_key", label_visibility="collapsed")

# 4. Řádek: Otočka
col1, col2 = st.columns([4, 3])
with col1:
    st.write("**🔄 Otočka?**")
with col2:
    je_otocka = st.segmented_control("Otočka", ["–", "Ano", "Ne"], key="je_otocka_key", label_visibility="collapsed")

# Věk pomocí segmentových tlačítek
st.write("**Věk:**")
vek = st.segmented_control(
    "Věk",
    ["Nezadán", "3–6", "7–12", "13–18", "19–30", "30–65", "60–75", "75+"],
    key="vek_key",
    label_visibility="collapsed"
)

# Skupina přesunutá dolů nad akční tlačítka
ve_skupine = st.checkbox("👥 Ve skupině s předchozím", key="ve_skupine_key")

# Poznámka a Sčítač
col_pozn, col_scit = st.columns(2)
with col_pozn:
    poznamka = st.text_input("Poznámka", placeholder="Poznámka...", key="poznamka_key", label_visibility="collapsed")
with col_scit:
    scitac = st.selectbox("Jméno sčítače", seznam_scitacu, key="vyber_scitace_widget", label_visibility="collapsed")

# --- FUNKCE PRO ZÁPIS A RESET ---
def zpracuj_kliknuti(smer):
    if scitac == "– (Vyber jméno sčítače)":
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

    # Načtení hodnot ze session_state
    v_ve_skupine = st.session_state.ve_skupine_key
    v_mod_dopravy = st.session_state.mod_dopravy_key
    v_vek = st.session_state.vek_key
    v_ma_psa = st.session_state.ma_psa_key
    v_ma_nakup = st.session_state.ma_nakup_key
    v_ma_aktovku = st.session_state.ma_aktovku_key
    v_je_otocka = st.session_state.je_otocka_key
    v_poznamka = st.session_state.poznamka_key

    je_skupina = False
    id_skupiny = None

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

    zaznam = {
        "Timestamp": timestamp_str,
        "Scitac": scitac,
        "Smer": smer,
        "Mod_pohybu": v_mod_dopravy,
        "Vek": v_vek if v_vek != "Nezadán" else None,
        "Pes": preved_stav(v_ma_psa),
        "Nakup": preved_stav(v_ma_nakup),
        "Aktovka": preved_stav(v_ma_aktovku),
        "Otocka": preved_stav(v_je_otocka),
        "Je_skupina": je_skupina,
        "ID_skupiny": id_skupiny,
        "Poznamka": v_poznamka if v_poznamka else None
    }
    
    st.session_state.scitani_data.append(zaznam)
    
    # Zápis do LocalStorage mobilu
    js_save = f"""
    <script>
    localStorage.setItem('scitani_backup', JSON.stringify({json.dumps(st.session_state.scitani_data)}));
    </script>
    """
    st.components.v1.html(js_save, height=0, width=0)
    
    # Plovoucí potvrzovací toast
    if smer == "prichod":
        st.toast(f"Zaznamenán PŘÍCHOD ({v_mod_dopravy})", icon="📥")
    else:
        st.toast(f"Zaznamenán ODCHOD ({v_mod_dopravy})", icon="📤")
        
    # Reset prvků zpět na výchozí stavy
    st.session_state.mod_dopravy_key = "Chodec 🚶"
    st.session_state.ve_skupine_key = False
    st.session_state.ma_psa_key = "–"
    st.session_state.ma_nakup_key = "–"
    st.session_state.ma_aktovku_key = "–"
    st.session_state.je_otocka_key = "–"
    st.session_state.vek_key = "Nezadán"
    st.session_state.poznamka_key = ""

# Zobrazení chybové hlášky
if st.session_state.get("chyba_scitace", False):
    st.error("❌ Před zaznamenáním průchodu musíte vybrat své JMÉNO SČÍTAČE!")

# --- AKČNÍ TLAČÍTKA ---
col_prichod, col_odchod = st.columns(2)

with col_prichod:
    st.button("🟢 PŘÍCHOD", use_container_width=True, type="primary", on_click=zpracuj_kliknuti, args=("prichod",))

with col_odchod:
    st.button("🔴 ODCHOD", use_container_width=True, type="primary", on_click=zpracuj_kliknuti, args=("odchod",))

# --- TLAČÍTKO PRO VYMAZÁNÍ PAMĚTI ---
def smazat_vsechno():
    st.session_state.scitani_data = []
    st.session_state.aktualni_id_skupiny = None

st.write("")
if st.button("🗑️ Vymazat historii a začít znova", use_container_width=True):
    smazat_vsechno()
    st.components.v1.html("<script>localStorage.removeItem('scitani_backup');</script>", height=0, width=0)
    st.rerun()

# --- EXPORT VÝSLEDKŮ ---
if st.session_state.scitani_data:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(3), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Stáhnout kompletní CSV", csv, "scitani_chodcu.csv", "text/csv", use_container_width=True)
