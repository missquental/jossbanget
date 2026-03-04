import streamlit as st
import time
import json
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
        with open(NOTE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Fungsi untuk menyimpan catatan ke file
def save_notes(content):
    with open(NOTE_FILE, "w", encoding="utf-8") as f:
        f.write(content)

# Judul aplikasi
st.title("📝 Notepad Live Realtime")

# Inisialisasi session state
if 'last_save_time' not in st.session_state:
    st.session_state.last_save_time = datetime.now()

# Fungsi callback saat teks berubah
def save_text():
    save_notes(st.session_state.text_area)
    st.session_state.last_save_time = datetime.now()

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

# Menampilkan informasi waktu terakhir disimpan
st.info(f"Terakhir disimpan: {st.session_state.last_save_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Tombol untuk membersihkan teks
if st.button("🗑️ Bersihkan"):
    save_notes("")
    st.session_state.last_save_time = datetime.now()
    st.experimental_rerun()

# Auto-refresh komponen text area setiap 20 detik
st.markdown("""
<script>
 setInterval(function() {
     var textAreas = document.querySelectorAll('textarea');
     if(textAreas.length > 0) {
         // Simulate a small change to trigger update
         var currentText = textAreas[0].value;
         textAreas[0].value = currentText;
     }
 }, 20000);
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("📝 Catatan Anda disimpan secara permanen dan input akan diperbarui setiap 20 detik")

# Menampilkan ukuran file
if os.path.exists(NOTE_FILE):
    file_size = os.path.getsize(NOTE_FILE)
    st.caption(f"Ukuran file: {file_size} bytes")
