import streamlit as st
import time
import json
import os
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Catatan Personal",
    page_icon="📝",
    layout="centered"
)

# Nama file untuk menyimpan catatan
NOTE_FILE = "notes.txt"

# Fungsi untuk membaca catatan dari file
def load_notes():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Fungsi untuk menyimpan catatan ke file
def save_notes(content):
    with open(NOTE_FILE, "w", encoding="utf-8") as f:
        f.write(content)

# Judul aplikasi
st.title("📝 Aplikasi Catatan Pribadi")

# Membaca catatan yang sudah ada
current_notes = load_notes()
if 'text' not in st.session_state:
    st.session_state.text = current_notes

# Fungsi callback saat teks berubah
def save_text():
    st.session_state.text = st.session_state.text_area
    save_notes(st.session_state.text)
    st.session_state.last_saved = datetime.now()

# Area teks dengan callback otomatis saat berubah
text_input = st.text_area(
    "Ketik catatan Anda di sini:",
    value=st.session_state.text,
    height=500,
    key="text_area",
    on_change=save_text
)

# Menampilkan informasi waktu terakhir disimpan
if 'last_saved' not in st.session_state:
    st.session_state.last_saved = datetime.now()

st.info(f"Terakhir disimpan: {st.session_state.last_saved.strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh setiap 20 detik
st.markdown('<meta http-equiv="refresh" content="20">', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("📝 Catatan Anda disimpan secara permanen dan akan diperbarui setiap 20 detik")

# Menampilkan ukuran file
if os.path.exists(NOTE_FILE):
    file_size = os.path.getsize(NOTE_FILE)
    st.caption(f"Ukuran file: {file_size} bytes")
