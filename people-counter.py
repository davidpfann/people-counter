# --- PARAMETRY NA JEDEN ŘÁDEK ---
# Použijeme sloupce, kde vlevo je text a vpravo tlačítka, vertikálně zarovnaná

# 1. Pes
r1_col1, r1_col2 = st.columns([1, 2])
with r1_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Pes? 🐕</b></div>", unsafe_html=True)
with r1_col2:
    ma_psa = st.radio("Pes", ["–", "Ano", "Ne"], horizontal=True, key="ma_psa_key", label_visibility="collapsed")

# 2. Nákup
r2_col1, r2_col2 = st.columns([1, 2])
with r2_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Nákup? 🛍️</b></div>", unsafe_html=True)
with r2_col2:
    ma_nakup = st.radio("Nákup", ["–", "Ano", "Ne"], horizontal=True, key="ma_nakup_key", label_visibility="collapsed")

# 3. Aktovka (ZDE BYLA TA CHYBA)
r3_col1, r3_col2 = st.columns([1, 2])
with r3_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Aktovka? 🎒</b></div>", unsafe_html=True)
with r3_col2:
    ma_aktovku = st.radio("Aktovka", ["–", "Ano", "Ne"], horizontal=True, key="ma_aktovku_key", label_visibility="collapsed")

# 4. Otočka
r4_col1, r4_col2 = st.columns([1, 2])
with r4_col1:
    st.markdown("<div style='padding-top: 5px;'><b>Otočka? 🔄</b></div>", unsafe_html=True)
with r4_col2:
    je_otocka = st.radio("Otočka", ["–", "Ano", "Ne"], horizontal=True, key="je_otocka_key", label_visibility="collapsed")
