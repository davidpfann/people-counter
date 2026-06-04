import datetime
import pandas as pd
import streamlit as st

st.set_page_config(layout="centered")

# Inicializace stavů aplikace
if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None


# --- LOGIKA ZÁPISU DO SKUPIN (Musí být definována před tlačítky!) ---
def zapis_zaznam(smer):
    nyni = datetime.datetime.now()
    timestamp_str = nyni.strftime("%Y-%m-%d %H:%M:%S")

    # Pomocná funkce na převod textu na True/False/None
    def preved_stav(hodnota):
        if hodnota == "Ano":
            return True
        if hodnota == "Ne":
            return False
        return None

    # Převod módu dopravy na text bez diakritiky pro čisté CSV
    mod_cisty = "Chodec"
    if "Běžec" in mod_dopravy:
        mod_cisty = "Bezec"
    elif "kole" in mod_dopravy:
        mod_cisty = "Kolo"
    elif "Koloběžka" in mod_dopravy:
        mod_cisty = "Kolobezka"

    # Převod věku na verzi bez diakritiky
    vek_map = {
        "– (Nezadano)": None,
        "Produktivni": "Produktivni",
        "Dite": "Dite",
        "Teenager": "Teenager",
        "Senior": "Senior",
    }
    vek_cisty = vek_map.get(vek, None)

    je_skupina = False
    id_skupiny = None

    if ve_skupine:
        je_skupina = True
        if st.session_state.aktualni_id_skupiny is not None:
            id_skupiny = st.session_state.aktualni_id_skupiny
        else:
            if st.session_state.scitani_data:
                posledni_index = len(st.session_state.scitani_data) - 1
                id_skupiny = st.session_state.scitani_data[posledni_index][
                    "Timestamp"
                ].replace(" ", "_")
                st.session_state.scitani_data[posledni_index][
                    "Je_skupina"
                ] = True
                st.session_state.scitani_data[posledni_index][
                    "ID_skupiny"
                ] = id_skupiny
                st.session_state.aktualni_id_skupiny = id_skupiny
            else:
                id_skupiny = timestamp_str.replace(" ", "_")
                st.session_state.aktualni_id_skupiny = id_skupiny
    else:
        st.session_state.aktualni_id_skupiny = None

    zaznam = {
        "Timestamp": timestamp_str,
        "Smer": smer,
        "Mod_pohybu": mod_cisty,
        "Vek": vek_cisty,
        "Pes": preved_stav(ma_psa),
        "Nakup": preved_stav(ma_nakup),
        "Aktovka": preved_stav(ma_aktovku),
        "Je_skupina": je_skupina,
        "ID_skupiny": id_skupiny,
        "Poznamka": poznamka if poznamka else None,
    }

    st.session_state.scitani_data.append(zaznam)
    info_skupina = f" (Skupina: {id_skupiny[-8:]})" if id_skupiny else ""
    st.toast(
        f"Zapsano: {mod_cisty} -> {smer.upper()}{info_skupina}",
        icon="👥" if je_skupina else "📝",
    )


# --- ROZHRANÍ: TLAČÍTKA SMĚRŮ NAHOŘE ---
col_tam, col_zpet = st.columns(2)

with col_tam:
    if st.button("⬅️ TAM", use_container_width=True, type="primary"):
        zapis_zaznam("tam")

with col_zpet:
    if st.button("ZPĚT ➡️", use_container_width=True, type="primary"):
        zapis_zaznam("zpet")

st.markdown("---")

# Volba módu dopravy (opravený label na prázdný řetězec)
mod_dopravy = st.radio(
    "", ["Chodec 🚶", "Běžec 🏃", "Na kole 🚴", "Koloběžka 🛴"], horizontal=True
)

# --- SEKCE PRO SKUPINY ---
ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", value=False)

# Pomocné třístavové parametry
c1, c2, c3 = st.columns(3)
with c1:
    ma_psa = st.segmented_control("Pes? 🐕", ["Ano", "–", "Ne"], default="–")
with c2:
    ma_nakup = st.segmented_control("Nákup? 🛍️", ["Ano", "–", "Ne"], default="–")
with c3:
    ma_aktovku = st.segmented_control(
        "Aktovka? 🎒", ["Ano", "–", "Ne"], default="–"
    )

vek = st.selectbox("Věk", ["– (Nezadano)", "Produktivni", "Dite", "Teenager", "Senior"])
poznamka = st.text_input("Obecná poznámka")

# --- EXPORT A ZOBRAZENÍ VÝSLEDKŮ ---
if st.session_state.scitani_data:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(5), use_container_width=True)

    # utf-8-sig zajistí správné otevření češtiny (např. z poznámek) v Excelu
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Stáhnout kompletní CSV",
        csv,
        "scitani_s_daty_skupin.csv",
        "text/csv",
        use_container_width=True,
    )
