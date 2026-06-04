import datetime
import pandas as pd
import streamlit as st

# POZNÁMKA PRO PROPOJENÍ S GOOGLE SHEETS:
# Pro ostré zálohování stačí odškrtnout (odcommentovat) řádky s st.connection níže.
try:
    from streamlit_gsheets import GSheetsConnection

    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

st.set_page_config(layout="centered")

if "scitani_data" not in st.session_state:
    st.session_state.scitani_data = []
if "aktualni_id_skupiny" not in st.session_state:
    st.session_state.aktualni_id_skupiny = None


def zapis_zaznam(smer):
    nyni = datetime.datetime.now()
    timestamp_str = nyni.strftime("%Y-%m-%d %H:%M:%S")

    def preved_stav(hodnota):
        if hodnota == "Ano":
            return True
        if hodnota == "Ne":
            return False
        return None

    # Rozšířené mapování módů dopravy na čistý text
    mod_cisty = "Chodec"
    if "Běžec" in mod_dopravy:
        mod_cisty = "Bezec"
    elif "kole" in mod_dopravy:
        mod_cisty = "Kolo"
    elif "Koloběžka" in mod_dopravy:
        mod_cisty = "Kolobezka"
    elif "Odrážedlo" in mod_dopravy:
        mod_cisty = "Odrazedlo"
    elif "Brusle" in mod_dopravy:
        mod_cisty = "Brusle"

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

    # AUTOMATICKÁ ZÁLOHA: Pokud je připojení aktivní, odešleme data hned online
    if conn is not None:
        try:
            df_aktualni = pd.DataFrame(st.session_state.scitani_data)
            conn.update(data=df_aktualni)
        except Exception:
            pass  # Pokud selže internet, aplikace pokračuje dál v offline režimu

    info_skupina = f" (Skupina: {id_skupiny[-8:]})" if id_skupiny else ""
    st.toast(
        f"Zapsano: {mod_cisty} -> {smer.upper()}{info_skupina}",
        icon="👥" if je_skupina else "📝",
    )


# --- ROZHRANÍ ---
col_tam, col_zpet = st.columns(2)
with col_tam:
    if st.button("⬅️ TAM", use_container_width=True, type="primary"):
        zapis_zaznam("tam")
with col_zpet:
    if st.button("ZPĚT ➡️", use_container_width=True, type="primary"):
        zapis_zaznam("zpet")

st.markdown("---")

# Rozšířené menu o odrážedlo a brusle
mod_dopravy = st.radio(
    "",
    [
        "Chodec 🚶",
        "Běžec 🏃",
        "Na kole 🚴",
        "Koloběžka 🛴",
        "Odrážedlo 🚲",
        "Brusle 🛼",
    ],
    horizontal=True,
)

ve_skupine = st.checkbox("👥 Šel/šla ve skupině s předchozím", value=False)

c1, c2, c3 = st.columns(3)
with c1:
    ma_psa = st.segmented_control("Pes? 🐕", ["Ano", "–", "Ne"], default="–")
with c2:
    ma_nakup = st.segmented_control("Nákup? 🛍️", ["Ano", "–", "Ne"], default="–")
with c3:
    ma_aktovku = st.segmented_control(
        "Aktovka? 🎒", ["Ano", "–", "Ne"], default="–"
    )

vek = st.selectbox("Věk", ["– (Nezadano)", "Produktivni", "Drite", "Teenager", "Senior"])
poznamka = st.text_input("Obecná poznámka")

if st.session_state.scitani_data:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.scitani_data)
    st.write(f"Celkem zaznamenáno průchodů: **{len(df)}**")
    st.dataframe(df.tail(5), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Stáhnout kompletní CSV",
        csv,
        "scitani_s_daty_skupin.csv",
        "text/csv",
        use_container_width=True,
    )
