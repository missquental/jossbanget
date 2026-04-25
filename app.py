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


# Fungsi callback saat teks berubah
def save_text():
    st.session_state.text = st.session_state.text_area
    save_notes(st.session_state.text)
    st.session_state.last_saved = datetime.now()
    # Update last modified manually after saving
    st.session_state.last_modified = os.path.getmtime(NOTE_FILE)

# Area teks dengan tombol refresh di atasnya
st.markdown("#### Catatan Anda:")

# Tombol refresh di sebelah label catatan
col1, col2 = st.columns([4, 1])
with col1:
    st.write("")  # Spacer
with col2:
    if st.button("🔄 Refresh", key="refresh_btn"):
        st.rerun()

# Area text input
text_input = st.text_area(
    "",
    value=st.session_state.text,
    height=500,
    key="text_area",
    on_change=save_text
)

# Menampilkan informasi waktu terakhir disimpan
st.info(f"Terakhir disimpan: {st.session_state.last_saved.strftime('%Y-%m-%d %H:%M:%S')}")

# Footer
st.markdown("---")
st.caption("📝 Catatan Anda disimpan secara permanen dan akan diperbarui hanya saat ada perubahan.")

# Menampilkan ukuran file
if os.path.exists(NOTE_FILE):
    file_size = os.path.getsize(NOTE_FILE)
    st.caption(f"Ukuran file: {file_size} bytes")
