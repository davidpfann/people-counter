import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="centered")

# Inicializace stavů aplikace
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None

# --- TLAČÍTKA SMĚRŮ ---
st.markdown("---")
col_tam, col_zpet = st.columns(2)

with col_tam:
    if st.button("⬅️ TAM", use_container_width=True, type="primary"):
        zapis_zaznam("tam")

with col_zpet:
    if st.button("ZPĚT ➡️", use_container_width=True, type="primary"):
        zapis_zaznam("zpet")

mod_dopravy = st.radio(["Chodec 🚶", "Běžec 🏃", "Na kole 🚴", "Koloběžka 🛴"], horizontal=True)

# --- NOVÁ SEKCE PRO SKUPINY ---
col_skupina = st.columns(1)[0]
with col_skupina:
    # Klíčový tag pro sčítače
    ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", value=False)

# Pomocné třístavové parametry z minula
c1, c2, c3 = st.columns(3)
with c1:
    ma_psa = st.segmented_control("Pes? 🐕", ["Ano", "–", "Ne"], default="–")
with c2:
    ma_nakup = st.segmented_control("Nákup? 🛍️", ["Ano", "–", "Ne"], default="–")
with c3:
    ma_aktovku = st.segmented_control("Aktovka? 🎒", ["Ano", "–", "Ne"], default="–")

vek = st.selectbox("Věk", ["– (Nezadáno)", "Produktivní", "Dítě", "Teenager", "Senior"])
poznamka = st.text_input("Obecná poznámka")

# --- LOGIKA ZÁPISU DO SKUPIN ---
def zapis_zaznam(smer):
    nyni = datetime.datetime.now()
    timestamp_str = nyni.strftime("%Y-%m-%d %H:%M:%S")
    
    # Pomocná funkce na převod textu na True/False/None
    def preved_stav(hodnota):
        if hodnota == "Ano": return True
        if hodnota == "Ne": return False
        return None

    je_skupina = False
    id_skupiny = None

    if ve_skupine:
        je_skupina = True
        # Pokud už skupina běží, vezmeme její stávající ID
        if st.session_state.aktualni_id_skupiny is not None:
            id_skupiny = st.session_state.aktualni_id_skupiny
        else:
            # Pokud sčítač klikl "ve skupině", ale předchozí záznam skupina nebyl,
            # musíme z něj zpětně udělat zakladatele skupiny (pokud existuje)
            if st.session_state.scitani_data:
                posledni_index = len(st.session_state.scitani_data) - 1
                # Vezmeme timestamp předchozího záznamu a uděláme z něj ID skupiny
                id_skupiny = st.session_state.scitani_data[posledni_index]["Timestamp"].replace(" ", "_")
                # Aktualizujeme předchozí záznam, že už patří do skupiny
                st.session_state.scitani_data[posledni_index]["Je_skupina"] = True
                st.session_state.scitani_data[posledni_index]["ID_skupiny"] = id_skupiny
                st.session_state.aktualni_id_skupiny = id_skupiny
            else:
                # Pokud je to úplně první záznam v aplikaci
                id_skupiny = timestamp_str.replace(" ", "_")
                st.session_state.aktualni_id_skupiny = id_skupiny
    else:
        # Pokud chodec není ve skupině, resetujeme ID skupiny v paměti pro příště
        st.session_state.aktualni_id_skupiny = None

    # Vytvoření samotného záznamu
    zaznam = {
        "Timestamp": timestamp_str,
        "Smer": smer,
        "Mod_pohybu": mod_dopravy,
        "Vek": vek if vek != "– (Nezadáno)" else None,
        "Pes": preved_stav(ma_psa),
        "Nakup": preved_stav(ma_nakup),
        "Aktovka": preved_stav(ma_aktovku),
        "Je_skupina": je_skupina,
        "ID_skupiny": id_skupiny,
        "Poznamka": poznamka if poznamka else None
    }
    
    st.session_state.scitani_data.append(zaznam)
    
    # Malé vizuální potvrzení na displeji
    info_skupina = f" (Skupina: {id_skupiny[-8:]})" if id_skupiny else ""
    st.toast(f"Zapsáno: {mod_dopravy} -> {smer.upper()}{info_skupina}", icon="👥" if je_skupina else "📝")

# --- EXPORT A ZOBRAZENÍ VÝSLEDKŮ ---
if st.session_state.scitani_data:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(5), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Stáhnout kompletní CSV", csv, "scitani_s_daty_skupin.csv", "text/csv", use_container_width=True)
