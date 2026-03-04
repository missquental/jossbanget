import streamlit as st
import time
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Notepad Live Realtime",
    page_icon="📝",
    layout="centered"
)

# Judul aplikasi
st.title("📝 Notepad Live Realtime")

# Inisialisasi session state untuk teks
if 'text' not in st.session_state:
    st.session_state.text = ""

# Fungsi untuk menyimpan teks ke session state
def save_text():
    st.session_state.text = st.session_state.text_area

# Area teks dengan callback otomatis saat berubah
text_input = st.text_area(
    "Ketik catatan Anda di sini:",
    value=st.session_state.text,
    height=300,
    key="text_area",
    on_change=save_text
)

# Menampilkan informasi waktu terakhir disimpan
st.info(f"Terakhir disimpan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Tombol untuk membersihkan teks
if st.button("🗑️ Bersihkan"):
    st.session_state.text = ""
    st.experimental_rerun()

# Auto-refresh setiap 5 detik
st.markdown('<meta http-equiv="refresh" content="5">', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("📝 Catatan Anda disimpan secara otomatis dan akan diperbarui setiap 5 detik")
