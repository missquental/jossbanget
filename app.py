import streamlit as st
import os
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Catatan Harian", page_icon="📝", layout="centered")

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

# Inisialisasi session state
if 'text' not in st.session_state:
    st.session_state.text = load_notes()

if 'last_modified' not in st.session_state:
    st.session_state.last_modified = None

if 'last_saved' not in st.session_state:
    st.session_state.last_saved = datetime.now()

# Cek apakah file berubah sejak kunjungan terakhir (deteksi eksternal)
current_mtime = os.path.getmtime(NOTE_FILE) if os.path.exists(NOTE_FILE) else 0

# Hanya update konten jika file berubah dari luar
if st.session_state.last_modified != current_mtime and st.session_state.last_modified is not None:
    st.session_state.text = load_notes()
    st.session_state.last_modified = current_mtime

# Judul aplikasi
st.title("📝 Aplikasi Catatan Sederhana")

# Fungsi callback saat teks berubah
def save_text():
    st.session_state.text = st.session_state.text_area
    save_notes(st.session_state.text)
    st.session_state.last_saved = datetime.now()
    # Update last modified manually after saving
    st.session_state.last_modified = os.path.getmtime(NOTE_FILE)

# Area teks dengan auto refresh
text_input = st.text_area(
    "Catatan Anda:",
    value=st.session_state.text,
    height=500,
    key="text_area",
    on_change=save_text
)

# Hidden button untuk trigger refresh dengan Enter
def trigger_refresh():
    st.rerun()

# Form untuk capture Enter key
with st.form(key='refresh_form', clear_on_submit=True):
    submit_button = st.form_submit_button(label='🔄 Refresh (Enter)', on_click=trigger_refresh)

# Menampilkan informasi waktu terakhir disimpan
st.info(f"Terakhir disimpan: {st.session_state.last_saved.strftime('%Y-%m-%d %H:%M:%S')}")

# Footer
st.markdown("---")
st.caption("📝 Catatan Anda disimpan secara permanen. Tekan Enter atau klik Refresh untuk memperbarui.")

# Menampilkan ukuran file
if os.path.exists(NOTE_FILE):
    file_size = os.path.getsize(NOTE_FILE)
    st.caption(f"Ukuran file: {file_size} bytes")
