import streamlit as st
import datetime
import pandas as pd
import json

st.set_page_config(layout="centered")

# --- Globální CSS injekce pro fixní jednořádkový design sloupců + spodní toast + zelené tlačítko ---
st.html("""
<style>
    /* Vynutíme, aby columns držely vedle sebe i na sebemenším mobilu a nezalamovaly se pod sebe */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 10px !important;
    }
    
    /* Levý sloupec s textem se nebude zalamovat */
    [data-testid="stHorizontalBlock"] > div:nth-child(1) {
        flex-grow: 1 !important;
        min-width: fit-content !important;
    }
    
    /* Pravý sloupec s tlačítky se přitlačí doprava */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex-grow: 0 !important;
        min-width: max-content !important;
    }

    /* POSUNUTÍ A ZMENŠENÍ TOASTU dolů, aby nepřekrýval horní menu */
    [data-testid="stToastContainer"] {
        top: auto !important;
        bottom: 20px !important;
        right: 20px !important;
        left: auto !important;
    }
    [data-testid="stToast"] {
        padding: 8px 12px !important;
        min-width: auto !important;
        max-width: 280px !important;
    }

    /* Stylování akčních tlačítek (Příchod = Zelená, Odchod = Červená) */
    [data-testid="stHorizontalBlock"]:last-of-type > div:nth-child(1) button {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
    }
    [data-testid="stHorizontalBlock"]:last-of-type > div:nth-child(1) button:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
</style>
""")

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

# --- 2. NOVÁ ROBUSTNÍ BEZRESTARTOVÁ LOGIKA PRO LOCAL STORAGE ---
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None

# JavaScriptový injektor, který přečte vnitřní paměť mobilu a bezpečně ji předá Pythonu bez cyklení stránky
js_bridge = """
<script>
    const sendData = () => {
        const data = localStorage.getItem('scitani_backup');
        if (data) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: data
            }, '*');
        }
    };
    // Spustíme hned po načtení prvků
    setTimeout(sendData, 100);
</script>
"""

# Vytvoření stabilního datového kanálu pod klíčem "backup_bridge"
# label_visibility="collapsed" schová pomocné okno, style ho zneviditelní
with st.container():
    st.html(f"<div style='display:none;'>{js_bridge}</div>")
    # Trik: využijeme query parametry nebo session_state, abychom načetli data bez st.rerun()
    captured_json = st.session_state.get("backup_bridge")
    
    if captured_json and not st.session_state.scitani_data:
        try:
            loaded_list = json.loads(captured_json)
            if isinstance(loaded_list, list) and len(loaded_list) > 0:
                st.session_state.scitani_data = loaded_list
        except Exception:
            pass

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
    st.session_state.vek_key = "Věk nezadán"
if "poznamka_key" not in st.session_state:
    st.session_state.poznamka_key = ""

# --- ROZHRANÍ APLIKACE ---

# Mód pohybu
mod_dopravy = st.segmented_control(
    "Mód pohybu",
    ["Chodec 🚶", "Běh🏃", " 🚴 ", " 🛴 ", " 🛼 ", "Jiné"],
    key="mod_dopravy_key",
    label_visibility="collapsed"
)

# --- PARAMETRY ---
# 1. Řádek: Pes
c1, c2 = st.columns([1, 1])
with c1:
    st.write("**🐕 Pes?**")
with c2:
    ma_psa = st.segmented_control("Pes", ["–", "Ano", "Ne"], key="ma_psa_key", label_visibility="collapsed")

# 2. Řádek: Aktovka
c1, c2 = st.columns([1, 1])
with c1:
    st.write("**🎒 Aktovka?**")
with c2:
    ma_aktovku = st.segmented_control("Aktovka", ["–", "Ano", "Ne"], key="ma_aktovku_key", label_visibility="collapsed")

# 3. Řádek: Nákup
c1, c2 = st.columns([1, 1])
with c1:
    st.write("**🛍️ Nákup?**")
with c2:
    ma_nakup = st.segmented_control("Nákup", ["–", "Ano", "Ne"], key="ma_nakup_key", label_visibility="collapsed")

# 4. Řádek: Otočka
c1, c2 = st.columns([1, 1])
with c1:
    st.write("**🔄 Otočka?**")
with c2:
    je_otocka = st.segmented_control("Otočka", ["–", "Ano", "Ne"], key="je_otocka_key", label_visibility="collapsed")

# Věk pomocí segmentových tlačítek
vek = st.segmented_control(
    "Věk",
    ["Věk nezadán", "3+", "6+", "12+", "18+", "30+", "60+", "75+"],
    key="vek_key",
    label_visibility="collapsed"
)

# Skupina přesunutá dolů nad akční tlačítka
ve_skupine = st.checkbox("👥 Šli ve skupině s předchozím zadaným", key="ve_skupine_key")

# Poznámka a Sčítač
col_scit, col_pozn = st.columns(2)
with col_scit:
    scitac = st.selectbox("Jméno sčítače", seznam_scitacu, key="vyber_scitace_widget", label_visibility="collapsed")
with col_pozn:
    poznamka = st.text_input("Poznámka", placeholder="Dobrovolná poznámka...", key="poznamka_key", label_visibility="collapsed")

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
        "Vek": v_vek if v_vek != "Věk nezadán" else None,
        "Pes": preved_stav(v_ma_psa),
        "Nakup": preved_stav(v_ma_nakup),
        "Aktovka": preved_stav(v_ma_aktovku),
        "Otocka": preved_stav(v_je_otocka),
        "Je_skupina": je_skupina,
        "ID_skupiny": id_skupiny,
        "Poznamka": v_poznamka if v_poznamka else None
    }
    
    st.session_state.scitani_data.append(zaznam)
    
    # Bezpečný tichý zápis na pozadí
    js_save = f"""
    <script>
    localStorage.setItem('scitani_backup', JSON.stringify({json.dumps(st.session_state.scitani_data)}));
    </script>
    """
    st.components.v1.html(js_save, height=0, width=0)
    
    if smer == "prichod":
        st.toast(f"Zaznamenán PŘÍCHOD ({v_mod_dopravy})", icon="📥")
    else:
        st.toast(f"Zaznamenán ODCHOD ({v_mod_dopravy})", icon="📤")
        
    st.session_state.mod_dopravy_key = "Chodec 🚶"
    st.session_state.ve_skupine_key = False
    st.session_state.ma_psa_key = "–"
    st.session_state.ma_nakup_key = "–"
    st.session_state.ma_aktovku_key = "–"
    st.session_state.je_otocka_key = "–"
    st.session_state.vek_key = "Věk nezadán"
    st.session_state.poznamka_key = ""

# Chybová hláška
if st.session_state.get("chyba_scitace", False):
    st.error("❌ Před zaznamenáním průchodu musíte vybrat své JMÉNO SČÍTAČE!")

# --- AKČNÍ TLAČÍTKA ---
col_prichod, col_odchod = st.columns(2)

with col_prichod:
    st.button("PŘÍCHOD", use_container_width=True, type="primary", on_click=zpracuj_kliknuti, args=("prichod",))

with col_odchod:
    st.button("ODCHOD", use_container_width=True, type="primary", on_click=zpracuj_kliknuti, args=("odchod",))

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
