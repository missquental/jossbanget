import streamlit as st
import time
import os
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Notepad Live Realtime",
    page_icon="📝",
    layout="centered"
)

# Nama file untuk menyimpan catatan
NOTE_FILE = "notes.txt"

# Fungsi untuk membaca catatan dari file
def load_notes():
    if os.path.exists(NOTE_FILE):
        try:
            with open(NOTE_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""
    return ""

# Fungsi untuk menyimpan catatan ke file
def save_notes(content):
    with open(NOTE_FILE, "w", encoding="utf-8") as f:
        f.write(content)

# Judul aplikasi
st.title("📝 Notepad Live Realtime")

# Inisialisasi session state
if 'last_check' not in st.session_state:
    st.session_state.last_check = time.time()

# Fungsi callback saat teks berubah
def save_text():
    save_notes(st.session_state.text_area)
    st.session_state.last_check = time.time()

# Membaca konten terbaru dari file
latest_content = load_notes()

# Area teks dengan callback otomatis saat berubah
text_input = st.text_area(
    "Ketik catatan Anda di sini:",
    value=latest_content,
    height=300,
    key="text_area",
    on_change=save_text
)

# Menampilkan informasi waktu terakhir diperbarui
last_update_time = datetime.fromtimestamp(st.session_state.last_check)
st.info(f"Terakhir diperbarui: {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Tombol untuk membersihkan teks
if st.button("🗑️ Bersihkan"):
    save_notes("")
    st.session_state.last_check = time.time()
    st.experimental_rerun()

# Auto-refresh textarea setiap 20 detik menggunakan JavaScript
st.markdown(f"""
<script>
let lastCheck = {st.session_state.last_check};
let currentTime = Date.now() / 1000;

// Cek apakah sudah lewat 20 detik
if ((currentTime - lastCheck) >= 20) {{
    // Kirim pesan ke parent window untuk refresh
    window.parent.postMessage({{type: 'streamlit:rerun'}}, '*');
}}
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("📝 Catatan Anda disimpan secara permanen dan textarea diperbarui setiap 20 detik")

# Menampilkan ukuran file
if os.path.exists(NOTE_FILE):
    file_size = os.path.getsize(NOTE_FILE)
    st.caption(f"Ukuran file: {file_size} bytes")

# Menampilkan debug info
st.caption(f"Debug - Last check: {st.session_state.last_check}")
