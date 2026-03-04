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

# Session state management
if 'last_check' not in st.session_state:
    st.session_state.last_check = time.time()

# Fungsi callback saat teks berubah
def save_text():
    save_notes(st.session_state.text_area)
    st.session_state.last_check = time.time()

# Membaca konten terbaru dari file
current_content = load_notes()

# Area teks dengan callback otomatis saat berubah
text_input = st.text_area(
    "Ketik catatan Anda di sini:",
    value=current_content,
    height=300,
    key="text_area",
    on_change=save_text
)

# Menampilkan timestamp
st.info(f"Terakhir update: {datetime.now().strftime('%H:%M:%S')}")

# Tombol aksi
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear"):
        save_notes("")
        st.experimental_rerun()

with col2:
    if st.button("🔄 Refresh"):
        st.experimental_rerun()

# AUTO-REFRESH LOGIC
current_time = time.time()
if current_time - st.session_state.last_check >= 20:
    st.session_state.last_check = current_time
    st.experimental_rerun()

# Visual countdown
time_passed = current_time - st.session_state.last_check
progress_value = min(time_passed / 20.0, 1.0)
st.progress(progress_value)
st.caption(f"Refresh otomatis dalam {max(0, 20-int(time_passed))} detik")

# Footer info
st.markdown("---")
st.caption("📝 Notes saved automatically • Refresh every 20 seconds")
