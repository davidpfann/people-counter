import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="centered")
st.title("Sčítání chodců: PŘÍCHOD / ODCHOD")

# Inicializace stavů aplikace v paměti
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None

st.subheader("Parametry chodce")

mod_dopravy = st.radio("Mód pohybu", ["Chodec 🚶", "Běžec 🏃", "Na kole 🚴", "Koloběžka 🛴"], horizontal=True)

# Sekce pro skupiny
ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", value=False)

st.subheader("Podrobné parametry (pokud je čas)")
st.caption("Pokud nestíháte, nechte nastavené '–' (Nezadáno).")

# Bezpečné řešení přepínačů pomocí st.radio s horizontálním rozložením
c1, c2, c3 = st.columns(3)
with c1:
    ma_psa = st.radio("Pes? 🐕", ["Ano", "–", "Ne"], index=1, horizontal=True)
with c2:
    ma_nakup = st.radio("Nákup? 🛍️", ["Ano", "–", "Ne"], index=1, horizontal=True)
with c3:
    ma_aktovku = st.radio("Aktovka? 🎒", ["Ano", "–", "Ne"], index=1, horizontal=True)

col_extra1, col_extra2 = st.columns(2)
with col_extra1:
    je_otocka = st.radio("Otočka/Návrat? 🔄", ["Ano", "–", "Ne"], index=1, horizontal=True)
with col_extra2:
    vek = st.selectbox("Věk", ["– (Nezadáno)", "Produktivní", "Dítě", "Teenager", "Senior"])

poznamka = st.text_input("Obecná poznámka")

# --- LOGIKA ZÁPISU (PŘÍCHOD / ODCHOD) ---
def zapis_zaznam(smer):
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
        "Smer": smer,  # Zapíše "prichod" nebo "odchod"
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
    
    info_skupina = f" (Skupina)" if je_skupina else ""
    st.toast(f"Zapsán {smer.upper()}: {mod_dopravy}{info_skupina}", icon="✅")

# --- AKČNÍ TLAČÍTKA (Čára smazána, texty upraveny) ---
col_prichod, col_odchod = st.columns(2)

with col_prichod:
    if st.button("📥 PŘÍCHOD", use_container_width=True, type="primary"):
        zapis_zaznam("prichod")

with col_odchod:
    if st.button("📤 ODCHOD", use_container_width=True, type="primary"):
        zapis_zaznam("odchod")

# --- EXPORT VÝSLEDKŮ ---
if st.session_state.scitani_data:
    st.markdown("---")  # Tato čára zůstává až nad výslednou tabulkou, kde nepřekáží
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(3), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Stáhnout kompletní CSV", csv, "scitani_chodcu.csv", "text/csv", use_container_width=True)
