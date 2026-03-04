import streamlit as st
import time
import os
from datetime import datetime
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="Form Jual Akun FB & Live Notepad",
    page_icon="📝",
    layout="wide"
)

# Nama file untuk menyimpan catatan
NOTE_FILE = "live_notes.txt"

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

# CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; }
body { font-family: 'Poppins', sans-serif; }
.main { padding: 20px; background: #f2f4ff; }
.container-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: row;
  gap: 20px;
}
.form-container {
  flex: 1;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  color: #fff;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.notepad-container {
  flex: 1.2;
  background: #fff;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  border: 1px solid #e0e6ed;
}
.form-header { text-align: center; margin-bottom: 25px; }
.form-header h2 { font-size: 26px; }
.stats-container {
  background: rgba(255,255,255,.15);
  padding: 15px;
  border-radius: 12px;
  text-align: center;
}
.stats-number { font-size: 30px; font-weight: 700; }
.refresh-btn {
  background: rgba(255,255,255,.25);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 15px;
  cursor: pointer;
}
.refresh-btn:hover { background: rgba(255,255,255,0.4); }
.form-group { margin-top: 18px; }
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
}
.form-group input {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-size: 15px;
}
.submit-btn {
  margin-top: 20px;
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
}
.notepad-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.notepad-header h3 {
  color: #333;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}
#syncStatus {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  background: #eee;
  color: #666;
}
.syncing { background: #fff4e5 !important; color: #b7791f !important; }
.synced { background: #e6fffa !important; color: #2c7a7b !important; }
textarea#liveNotepad {
  width: 100%;
  height: 300px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 15px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  resize: vertical;
  outline: none;
  background: #f8fafc;
  color: #1a202c;
  line-height: 1.6;
}
.result-message {
  margin-top: 15px;
  padding: 12px;
  border-radius: 10px;
  text-align: center;
}
.success-message { background: rgba(46,204,113,.25); color: #2ecc71; }
.error-message { background: rgba(231,76,60,.25); color: #e74c3c; }
@media (max-width: 768px) {
  .container-wrapper { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)

# Judul halaman
st.markdown("<h1 style='text-align: center; color: #333;'>🔐 Form Jual Akun FB & 📝 Live Notepad</h1>", unsafe_allow_html=True)

# Layout dengan dua kolom
col1, col2 = st.columns([1, 1.2])

# ================= FORM SECTION =================
with col1:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Header form
    st.markdown('<div class="form-header"><h2>🔐 Jual Akun FB</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12px; opacity: 0.8;">Data otomatis tersimpan ke Spreadsheet</p></div>', unsafe_allow_html=True)
    
    # Stats container
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.markdown('<div class="stats-number">0</div>', unsafe_allow_html=True)
    st.markdown('Ready Akun FB', unsafe_allow_html=True)
    if st.button("🔄 Refresh", key="refresh_stats"):
        st.info("Fitur refresh stats akan terhubung ke database")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Form
    with st.form("data_form"):
        uid = st.text_input("👤 UID", placeholder="Contoh: 1000...")
        email = st.text_input("📧 Email", placeholder="email@end.tw")
        
        st.markdown("👩 Generate Nama & Email", unsafe_allow_html=True)
        if st.form_submit_button("🎲 Generate Random"):
            st.info("Fitur generate nama akan diimplementasikan")
            
        st.markdown('<div style="margin-top:8px;font-size:12px; display:flex; justify-content: space-between;">', unsafe_allow_html=True)
        st.markdown('<span>Sisa kombinasi:</span><b><span>0</span></b></div>', unsafe_allow_html=True)
        
        password = st.text_input("🔒 Password", type="password")
        
        submitted = st.form_submit_button("🚀 Kirim ke Database")
        if submitted:
            if uid and email and password:
                st.success("✅ Data berhasil terkirim!")
            else:
                st.error("❌ Harap lengkapi semua field!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================= LIVE NOTEPAD SECTION =================
with col2:
    st.markdown('<div class="notepad-container">', unsafe_allow_html=True)
    
    # Header notepad
    st.markdown('<div class="notepad-header">', unsafe_allow_html=True)
    st.markdown('<h3>📝 Live Notepad Share</h3>', unsafe_allow_html=True)
    status_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p style="font-size: 12px; color: #718096; margin-bottom: 10px;">Catatan ini dibagikan ke semua admin secara real-time. Hati-hati saat menghapus.</p>', unsafe_allow_html=True)
    
    # Session state untuk tracking waktu
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    if 'last_updated' not in st.session_state:
        st.session_state.last_updated = time.time()
    
    # Membaca konten terbaru
    latest_content = load_notes()
    
    # Text area dengan callback
    def save_text():
        save_notes(st.session_state.live_notepad)
        st.session_state.last_updated = time.time()
        status_placeholder.markdown(f'<span id="syncStatus" class="synced">Tersimpan</span>', unsafe_allow_html=True)
    
    # Status sync awal
    status_placeholder.markdown(f'<span id="syncStatus" class="synced">Terhubung</span>', unsafe_allow_html=True)
    
    # Text area
    note_content = st.text_area(
        "",
        value=latest_content,
        height=300,
        key="live_notepad",
        on_change=save_text,
        placeholder="Tulis catatan penting di sini..."
    )
    
    # Menampilkan waktu terakhir update
    st.markdown(f'<div style="margin-top: 10px; font-size: 11px; color: #a0aec0; text-align: right;">Terakhir diubah: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-refresh logic
    current_time = time.time()
    time_since_refresh = current_time - st.session_state.last_refresh
    
    if time_since_refresh >= 20:
        st.session_state.last_refresh = current_time
        st.experimental_rerun()
    
    # Progress bar untuk visual feedback
    progress = min(time_since_refresh / 20.0, 1.0)
    st.progress(progress)
    remaining_time = max(0, 20 - int(time_since_refresh))
    st.caption(f"Auto-refresh dalam {remaining_time} detik")

# Footer
st.markdown("---")
st.caption("📝 Notes saved automatically • Refresh every 20 seconds")

# Debug info (opsional)
if st.checkbox("🔍 Show debug info"):
    st.write(f"Last refresh: {st.session_state.last_refresh}")
    st.write(f"Time diff: {time_since_refresh}")
    st.write(f"File size: {os.path.getsize(NOTE_FILE) if os.path.exists(NOTE_FILE) else 0} bytes")
