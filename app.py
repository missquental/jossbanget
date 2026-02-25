import sys
import subprocess
import threading
import time
import os
import json
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import urllib.parse
import requests
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import base64

# --- INSTALL DEPENDENCIES (Guaranteed) ---
def ensure_dependencies():
    packages = ["streamlit", "google-auth", "google-auth-oauthlib", "google-api-python-client", "pandas", "plotly"]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure_dependencies()

import streamlit as st

# --- MODERN CSS (Keep-Alive & Modern Design) ---
def add_custom_css():
    st.markdown("""
    <style>
    /* Global Reset & Colors */
    :root {
        --primary-color: #4361ee;
        --secondary-color: #3f37c9;
        --accent-color: #4cc9f0;
        --success-color: #4caf50;
        --warning-color: #ff9800;
        --error-color: #f44336;
        --background-color: #f8f9fa;
        --card-bg: #ffffff;
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --border-radius: 12px;
        --shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #121212;
            --card-bg: #1e1e1e;
            --text-primary: #e0e0e0;
            --text-secondary: #b0b0b0;
        }
    }

    /* Main Layout */
    .main { background-color: var(--background-color); padding: 1rem; }

    h1, h2, h3 { color: var(--text-primary); font-weight: 600; }

    /* Status Badge (Heartbeat) */
    .heartbeat-status {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        animation: pulse-green 2s infinite;
    }

    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(20, 128, 60, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(20, 128, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(20, 128, 60, 0); }
    }

    /* Cards */
    .stCard { background-color: var(--card-bg); border-radius: var(--border-radius); box-shadow: var(--shadow); padding: 1.5rem; margin-bottom: 1rem; }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary-color); color: white; border: none; border-radius: 8px; padding: 0.6rem 1rem; font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: var(--secondary-color); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(67, 97, 238, 0.3); }
    .stButton>button:active { transform: translateY(0); }

    .stButton>button[kind="primary"] { background-color: var(--success-color); }
    .stButton>button[kind="secondary"] { background-color: var(--text-secondary); }

    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>select { border-radius: 8px; border: 1px solid #ced4da; padding: 0.5rem; }

    /* Tabs & Expander */
    .stTabs [data-baseweb="tab"] { background-color: var(--card-bg); border-radius: 8px 8px 0 0; }
    .streamlit-expanderHeader { background-color: var(--card-bg); border-radius: 8px; padding: 0.5rem 1rem !important; }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .stButton>button { width: 100%; margin-bottom: 5px; }
        .grid-container { grid-template-columns: 1fr !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE HANDLING ---
def init_database():
    try:
        db_path = Path("streaming_logs.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaming_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                log_type TEXT NOT NULL,
                message TEXT NOT NULL,
                video_file TEXT,
                stream_key TEXT,
                channel_name TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT UNIQUE NOT NULL,
                channel_id TEXT NOT NULL,
                auth_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaming_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                video_file TEXT
            )
        ''')

        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database Error: {e}")

def save_channel_auth(channel_name, channel_id, auth_data):
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO saved_channels 
            (channel_name, channel_id, auth_data, created_at, last_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (channel_name, channel_id, json.dumps(auth_data), datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Save Auth Error: {e}")
        return False

def load_saved_channels():
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        cursor.execute('SELECT channel_name, channel_id, auth_data, last_used FROM saved_channels ORDER BY last_used DESC')
        channels = []
        for row in cursor.fetchall():
            channels.append({'name': row[0], 'id': row[1], 'auth': json.loads(row[2]), 'last_used': row[3]})
        conn.close()
        return channels
    except Exception as e:
        st.error(f"Load Auth Error: {e}")
        return []

def log_to_database(session_id, log_type, message, video_file=None, stream_key=None, channel_name=None):
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        cursor.execute('INSERT INTO streaming_logs (timestamp, session_id, log_type, message, video_file, stream_key, channel_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (datetime.now().isoformat(), session_id, log_type, message, video_file, stream_key, channel_name))
        conn.commit()
        conn.close()
    except Exception as e:
        pass # Silent fail for logging to avoid crashing

def get_logs_from_database(session_id=None, limit=50):
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        if session_id:
            cursor.execute('SELECT timestamp, log_type, message FROM streaming_logs WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?', (session_id, limit))
        else:
            cursor.execute('SELECT timestamp, log_type, message FROM streaming_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    except Exception as e:
        return []

# --- GOOGLE OAUTH & YOUTUBE API ---
try:
    import google.auth
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-auth", "google-auth-oauthlib", "google-api-python-client"])
    import google.auth
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

PREDEFINED_OAUTH_CONFIG = {
    "web": {
        "client_id": "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com",
        "project_id": "anjelikakozme",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_secret": "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",
        "redirect_uris": ["https://redirect1x.streamlit.app"]
    }
}

def create_youtube_service(credentials_dict):
    try:
        credentials = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret'),
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        return build('youtube', 'v3', credentials=credentials)
    except Exception as e:
        st.error(f"YT Service Error: {e}")
        return None

def get_channel_info(service):
    try:
        request = service.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        st.error(f"Channel Info Error: {e}")
        return []

def generate_auth_url(client_config):
    try:
        scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
        auth_url = (
            f"{client_config['auth_uri']}?"
            f"client_id={client_config['client_id']}&"
            f"redirect_uri={urllib.parse.quote(client_config['redirect_uris'][0])}&"
            f"scope={urllib.parse.quote(' '.join(scopes))}&"
            f"response_type=code&access_type=offline&prompt=consent"
        )
        return auth_url
    except Exception as e:
        st.error(f"Auth URL Error: {e}")
        return None

def exchange_code_for_tokens(client_config, auth_code):
    try:
        token_data = {
            'client_id': client_config['client_id'],
            'client_secret': client_config['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': client_config['redirect_uris'][0]
        }
        response = requests.post(client_config['token_uri'], data=token_data)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Token Exchange Error: {e}")
        return None

def create_live_stream(service, title, description, scheduled_start_time, privacy_status="public", made_for_kids=False):
    try:
        # 1. Create Stream
        stream_request = service.liveStreams().insert(part="snippet,cdn", body={
            "snippet": {"title": title},
            "cdn": {"resolution": "1080p", "frameRate": "30fps", "ingestionType": "rtmp"}
        })
        stream_response = stream_request.execute()

        # 2. Create Broadcast
        broadcast_body = {
            "snippet": {"title": title, "description": description, "scheduledStartTime": scheduled_start_time.isoformat()},
            "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": made_for_kids, "enableAutoStart": True},
            "contentDetails": {"enableAutoStart": True, "enableAutoStop": True, "recordFromStart": True, "enableEmbed": True}
        }

        broadcast_request = service.liveBroadcasts().insert(part="snippet,status,contentDetails", body=broadcast_body)
        broadcast_response = broadcast_request.execute()

        # 3. Bind
        service.liveBroadcasts().bind(id=broadcast_response['id'], part="id,contentDetails", streamId=stream_response['id']).execute()

        return {
            "stream_key": stream_response['cdn']['ingestionInfo']['streamName'],
            "stream_url": stream_response['cdn']['ingestionInfo']['ingestionAddress'],
            "broadcast_id": broadcast_response['id'],
            "watch_url": f"https://www.youtube.com/watch?v={broadcast_response['id']}",
            "studio_url": f"https://studio.youtube.com/video/{broadcast_response['id']}/livestreaming"
        }
    except Exception as e:
        st.error(f"Create Live Error: {e}")
        return None

# --- FFmpeg Streaming ---
def get_video_duration(video_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, text=True
        )
        return float(result.stdout.strip()) if result.stdout.strip() else None
    except Exception:
        return None

def run_ffmpeg(video_path, stream_key, log_callback, session_id=None, duration_limit=None):
    output_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", video_path,
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", "2500k", "-maxrate", "2500k",
        "-bufsize", "5000k", "-r", "30", "-g", "60", "-keyint_min", "60",
        "-c:a", "aac", "-b:a", "128k", "-f", "flv", output_url
    ]
    if duration_limit:
        cmd = ["ffmpeg", "-t", str(duration_limit), "-re", "-stream_loop", "-1", "-i", video_path] + cmd[5:]

    log_callback("🚀 FFmpeg started...")
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            log_callback(line.strip())
            if session_id: log_to_database(session_id, "FFMPEG", line.strip(), video_path)
        process.wait()
        log_callback("✅ FFmpeg finished.")
        if session_id: log_to_database(session_id, "INFO", "Streaming session ended", video_path)
    except Exception as e:
        log_callback(f"❌ FFmpeg Error: {e}")
        if session_id: log_to_database(session_id, "ERROR", f"FFmpeg Error: {e}", video_path)

# --- MAIN APP LOGIC ---
def main():
    # --- CONFIGURATION ---
    st.set_page_config(page_title="YT Live Master", page_icon="📺", layout="wide")
    add_custom_css()

    # --- INITIALIZATION ---
    init_database()
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if 'youtube_service' not in st.session_state:
        st.session_state['youtube_service'] = None
    if 'channel_info' not in st.session_state:
        st.session_state['channel_info'] = None

    # --- HEARTBEAT LOGIC (KEEP-ALIVE SERVER SIDE) ---
    if 'last_heartbeat' not in st.session_state:
        st.session_state['last_heartbeat'] = time.time()
    if time.time() - st.session_state['last_heartbeat'] > 60:
        log_to_database(st.session_state['session_id'], "HEARTBEAT", "✅ Keep-Alive Signal Active (Server Running)", None)
        st.session_state['last_heartbeat'] = time.time()

    # --- META REFRESH (KEEP-ALIVE CLIENT SIDE) ---
    # Refresh every 180 seconds (3 minutes) to prevent idle timeout
    st.markdown(f"<meta http-equiv='refresh' content='180'>", unsafe_allow_html=True)

    # --- HEADER & STATUS ---
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem; background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%); border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 8px 20px rgba(0,0,0,0.2);">
        <h1 style="color:white; margin:0;">🎥 YouTube Live Streaming Master</h1>
        <p style="color:rgba(255,255,255,0.85);">Professional Multi-Batch Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Status Badge
    st.markdown('<div class="heartbeat-status">🟢 SYSTEM STATUS: ONLINE & MONITORED</div>', unsafe_allow_html=True)

    # Auto-Refresh Info
    st.info("🔔 **Auto-Refresh Active:** Browser akan reload otomatis setiap 3 menit agar session tetap aktif.", icon="ℹ️")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"🆔 Session: {st.session_state['session_id']}")

        # Saved Channels
        st.subheader("💾 Saved Channels")
        saved_channels = load_saved_channels()
        if saved_channels:
            for ch in saved_channels:
                st.write(f"📺 {ch['name']} (Last: {ch['last_used'][:10]})")
                if st.button("🔑 Load", key=f"load_{ch['name']}"):
                    service = create_youtube_service(ch['auth'])
                    if service:
                        channels = get_channel_info(service)
                        if channels:
                            st.session_state['youtube_service'] = service
                            st.session_state['channel_info'] = channels[0]
                            st.success(f"✅ Loaded: {channels[0]['snippet']['title']}")
                            st.rerun()
        else:
            st.info("No saved channels.")

        # Auth Section
        st.subheader("🔐 Google OAuth Setup")
        if st.button("🔑 Use Predefined OAuth Config"):
            st.session_state['oauth_config'] = PREDEFINED_OAUTH_CONFIG['web']
            st.success("✅ Predefined Config Loaded!")
            st.rerun()

        if 'oauth_config' in st.session_state:
            auth_url = generate_auth_url(st.session_state['oauth_config'])
            if auth_url:
                st.markdown("### 🔗 Authorization Link")
                st.markdown(f"[Click to Authorize]({auth_url})")

                auth_code = st.text_input("Or paste code:", type="password")
                if st.button("🔄 Exchange Code"):
                    if auth_code:
                        tokens = exchange_code_for_tokens(st.session_state['oauth_config'], auth_code)
                        if tokens:
                            creds = {
                                'access_token': tokens['access_token'],
                                'refresh_token': tokens.get('refresh_token'),
                                'token_uri': st.session_state['oauth_config']['token_uri'],
                                'client_id': st.session_state['oauth_config']['client_id'],
                                'client_secret': st.session_state['oauth_config']['client_secret']
                            }
                            service = create_youtube_service(creds)
                            if service:
                                channels = get_channel_info(service)
                                if channels:
                                    st.session_state['youtube_service'] = service
                                    st.session_state['channel_info'] = channels[0]
                                    save_channel_auth(channels[0]['snippet']['title'], channels[0]['id'], creds)
                                    st.success(f"✅ Connected: {channels[0]['snippet']['title']}")
                                    st.rerun()
        else:
            st.info("Upload OAuth JSON or use Predefined config above.")

        # Logs
        st.subheader("📊 Logs")
        if st.button("🔄 Refresh Logs"):
            st.rerun()
        logs = get_logs_from_database(st.session_state['session_id'], 20)
        for log in logs:
            if log[1] == "HEARTBEAT":
                st.success(f"✅ {log[0]}: {log[2]}")
            elif log[1] == "ERROR":
                st.error(f"❌ {log[0]}: {log[2]}")
            else:
                st.text(f"ℹ️ {log[0]}: {log[2]}")

    # --- MAIN CONTENT ---
    col1, col2 = st.columns([3, 1])

    # --- LEFT COLUMN: SETUP ---
    with col1:
        st.markdown('<div class="card-header"><h2>🎥 Video & Setup</h2></div>', unsafe_allow_html=True)

        # Video Upload
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.flv', '.avi', '.mov', '.mkv'))]
        if video_files:
            selected_video = st.selectbox("Select Video File", video_files)
            video_path = selected_video
        else:
            uploaded_file = st.file_uploader("Upload Video", type=['mp4'])
            video_path = None
            if uploaded_file:
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                video_path = uploaded_file.name
                st.success(f"✅ {uploaded_file.name} uploaded.")

        if 'youtube_service' in st.session_state:
            st.markdown('<div class="card-header"><h2>📺 YouTube Live Control</h2></div>', unsafe_allow_html=True)

            stream_title = st.text_input("Stream Title", "Live Stream - Auto Start")
            privacy = st.selectbox("Privacy", ["public", "unlisted", "private"])

            if st.button("🚀 Auto Create & Start", type="primary", key="btn_start"):
                if not video_path:
                    st.error("❌ Please upload or select a video first!")
                else:
                    with st.spinner("Creating YouTube Live Broadcast..."):
                        # Schedule for 10 seconds from now
                        scheduled_time = datetime.now() + timedelta(seconds=10)
                        live_info = create_live_stream(
                            st.session_state['youtube_service'],
                            stream_title,
                            "Auto-started by Streamlit App",
                            scheduled_time,
                            privacy
                        )

                        if live_info:
                            st.success("🎉 YouTube Live Created!")
                            st.session_state['current_stream_key'] = live_info['stream_key']
                            st.info(f"📺 Watch URL: {live_info['watch_url']}")

                            # Start FFmpeg
                            def log_callback(msg):
                                st.session_state['live_log'] = msg

                            # Save session
                            save_streaming_session(st.session_state['session_id'], video_path)

                            # Start Streaming Thread
                            st.session_state['streaming'] = True
                            ffmpeg_thread = threading.Thread(
                                target=run_ffmpeg, 
                                args=(video_path, live_info['stream_key'], log_callback, st.session_state['session_id'], None), 
                                daemon=True
                            )
                            ffmpeg_thread.start()
                            st.success("🚀 Streaming Started!")
                            st.rerun()
        else:
            st.info("🔑 Connect YouTube first using the sidebar.")

    # --- RIGHT COLUMN: STATUS & LOGS ---
    with col2:
        st.markdown('<div class="card-header"><h2>📊 Status</h2></div>', unsafe_allow_html=True)

        if st.session_state.get('streaming', False):
            st.markdown('<div style="text-align:center; padding: 1rem; background: #d4edda; border-radius: 8px; color: #155724; font-weight: bold;">🔴 LIVE NOW</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center; padding: 1rem; background: #e2e3e5; border-radius: 8px; color: #383d41; font-weight: bold;">OFFLINE</div>', unsafe_allow_html=True)

        if 'current_stream_key' in st.session_state:
            st.code(st.session_state['current_stream_key'], language=None)
            if st.button("⏹️ Stop Streaming"):
                os.system("pkill -f ffmpeg")
                st.session_state['streaming'] = False
                st.success("Streaming stopped.")
                st.rerun()

        st.markdown("---")
        st.subheader("📝 Recent Logs")
        logs = get_logs_from_database(st.session_state['session_id'], 15)
        if logs:
            for log in logs:
                st.text(f"[{log[0][-8:]}] {log[2]}")
        else:
            st.text("No logs yet.")

    # --- BOTTOM: LIVE LOGS AUTO-REFRESH ---
    if st.session_state.get('streaming', False):
        time.sleep(3)
        st.rerun()

# Helper for saving session
def save_streaming_session(session_id, video_path):
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        cursor.execute('INSERT INTO streaming_sessions (session_id, start_time, video_file) VALUES (?, ?, ?)',
                       (session_id, datetime.now().isoformat(), video_path))
        conn.commit()
        conn.close()
    except Exception:
        pass

if __name__ == "__main__":
    main()
