import streamlit as st

# ... předchozí kód (Chodec, Běžec...)

# 1. Řádek: Pes
col1, col2 = st.columns([1, 1])  # Rozdělení na poloviny, případně [2, 3] podle potřeby
with col1:
    st.markdown("### 🐶 Pes?")  # Použij markdown pro hezké zarovnání
with col2:
    # label="" skryje vestavěný popisek, aby nezabíral místo nad tlačítky
    pes = st.radio("", ["-", "Ano", "Ne"], horizontal=True, label_visibility="collapsed")

# 2. Řádek: Školní aktovka
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🎒 Školní aktovka?")
with col2:
    aktovka = st.radio("", ["-", "Ano", "Ne"], horizontal=True, label_visibility="collapsed")

# 3. Řádek: Nákup
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🛍️ Nákup?")
with col2:
    nakup = st.radio("", ["-", "Ano", "Ne"], horizontal=True, label_visibility="collapsed")

# 4. Řádek: Otočka/Návrat
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🔄 Otočka/Návrat?")
with col2:
    otocka = st.radio("", ["-", "Ano", "Ne"], horizontal=True, label_visibility="collapsed")
