"""
🗺️ WebGIS Pemanfaatan Ruang - ULTIMATE FIX dengan JavaScript
Logo: D:\TUGAS AKHIR\CODING\logoupimerah.png
FIXED: Selectbox text color dengan JavaScript injection
"""

import os
import io
import time
import base64
import zipfile
import tempfile
import pathlib
from pathlib import Path
from PIL import Image

import geopandas as gpd
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import leafmap.foliumap as leafmap

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCOPES    = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = st.secrets.get("FOLDER_ID", "1dTdLnvUyRgFDKCSLLKH83ZOb2fou0Mci")

TEMP_DIR = pathlib.Path(tempfile.gettempdir()) / "webgis_cache"
TEMP_DIR.mkdir(exist_ok=True)

DATA_FILE       = TEMP_DIR / "DATA PEMANFAATAN.geojson"
UPLOADED_DATA_FILE = TEMP_DIR / "data_uploaded.geojson"  # TERPISAH!
KABUPATEN_FILE  = TEMP_DIR / "Batas Administrasi Kabupaten Bandung.geojson"
KECAMATAN_FILE  = TEMP_DIR / "Batas Administrasi Kecamatan Katapang.geojson"
RTRW_FILE       = TEMP_DIR / "RTRW.geojson"

from pathlib import Path

BASE_DIR = Path(__file__).parent

LOGO_PATH = BASE_DIR / "logoupimerah.png"

DATA_PEMANFAATAN = BASE_DIR / "DATA PEMANFAATAN.geojson"
BATAS_KAB = BASE_DIR / "Batas Administrasi Kabupaten Bandung.geojson"
BATAS_KEC = BASE_DIR / "Batas Administrasi Kecamatan Katapang.geojson"
RTRW = BASE_DIR / "RTRW.geojson"

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")

st.set_page_config(page_title="WebGIS Pemanfaatan Ruang", page_icon="🗺️", layout="wide", initial_sidebar_state="collapsed")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 CSS STYLING - DENGAN JAVASCRIPT INJECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --navy: #1a3a52;
    --gold: #FFD700;
    --gold-dark: #D4A500;
    --teal: #00BCD4;
    --coral: #FF6B6B;
    --white: #ffffff;
    --gray-light: #f0f2f5;
    --gray-lighter: #fafbfc;
    --text-dark: #2c3e50;
}

* { box-sizing: border-box; }
html, body { 
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important;
}

.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important; }

/* ════════════════════════════════════════════════════════════════ */
/* 🔥 HEADER - LIGHT & CLEAN                                        */
/* ════════════════════════════════════════════════════════════════ */

.header-gold-bar {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafb 50%, #f0f4f8 100%);
    padding: 16px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 85px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    position: sticky;
    top: 0;
    z-index: 999;
    width: 100%;
    border-bottom: 3px solid;
    border-image: linear-gradient(90deg, #FFD700, #00BCD4) 1;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 0.3;
}

.header-logo-img {
    max-width: 65px;
    height: auto;
    max-height: 65px;
    object-fit: contain;
    filter: drop-shadow(0 2px 8px rgba(255, 215, 0, 0.2));
    transition: all 0.3s ease;
}

.header-logo-img:hover {
    filter: drop-shadow(0 4px 12px rgba(255, 215, 0, 0.4));
    transform: scale(1.05);
}

.header-logo-placeholder {
    width: 58px;
    height: 58px;
    background: linear-gradient(135deg, #FFD700, #00BCD4);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    font-weight: bold;
    color: white;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.25);
    animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 4px 12px rgba(255, 215, 0, 0.25); }
    50% { box-shadow: 0 4px 16px rgba(0, 188, 212, 0.3); }
}

.header-right {
    display: flex;
    gap: 12px;
    flex: 0.7;
    justify-content: flex-end;
}

.nav-btn-group button {
    background: linear-gradient(135deg, #1a3a52, #2a5a72) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    cursor: pointer;
    white-space: nowrap;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    position: relative;
    overflow: hidden;
}

.nav-btn-group button:hover {
    background: linear-gradient(135deg, #FFD700, #FFC700) !important;
    color: #1a3a52 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 20px rgba(255, 215, 0, 0.3) !important;
}

.nav-btn-group button:active {
    transform: translateY(-1px) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🎨 HERO SECTION - LIGHT GRADIENT                                */
/* ════════════════════════════════════════════════════════════════ */

.hero-section {
    background: linear-gradient(135deg, #1a3a52 0%, #2a5a72 25%, #1a4a5f 50%, #0f3a4a 75%, #1a3a52 100%);
    color: white;
    padding: 90px 60px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin: 0;
    min-height: 320px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(0, 188, 212, 0.15) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 6s ease-in-out infinite;
}

.hero-section::after {
    content: '';
    position: absolute;
    bottom: -50%;
    left: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(255, 215, 0, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 8s ease-in-out infinite reverse;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-30px); }
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 1000px;
}

.hero-icon {
    font-size: 60px;
    margin-bottom: 20px;
    display: inline-block;
    animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 800;
    margin: 12px 0;
    letter-spacing: 2px;
    text-transform: uppercase;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    line-height: 1.2;
}

.hero-title::first-letter {
    color: #FFD700;
}

.hero-subtitle {
    font-size: 1rem;
    line-height: 1.8;
    opacity: 0.95;
    font-weight: 300;
    letter-spacing: 0.5px;
    max-width: 900px;
    margin: 16px auto 0;
    color: #00BCD4;
}

/* ════════════════════════════════════════════════════════════════ */
/* 📦 MAIN CONTAINER                                               */
/* ════════════════════════════════════════════════════════════════ */

.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 50px 40px;
    background: transparent;
}

/* ════════════════════════════════════════════════════════════════ */
/* 📍 SECTION HEADER - LIGHT THEME                                 */
/* ════════════════════════════════════════════════════════════════ */

.section-header {
    text-align: center;
    margin-bottom: 40px;
    padding-bottom: 20px;
    position: relative;
}

.section-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, #FFD700, #00BCD4);
    border-radius: 2px;
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 800;
    color: #1a3a52;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 2px;
    position: relative;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🎯 FEATURE BOX - COMPACT & LIGHT                               */
/* ════════════════════════════════════════════════════════════════ */

.feature-box {
    background: white;
    border-radius: 14px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    border: 1.5px solid #e8ecf1;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    overflow: hidden;
}

.feature-box::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(255, 215, 0, 0.08) 0%, transparent 70%);
    transition: all 0.4s ease;
}

.feature-box:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 12px 30px rgba(26, 58, 82, 0.12);
    border-color: #FFD700;
}

.feature-box:hover::before {
    top: -20%;
    right: -20%;
}

.feature-icon {
    font-size: 3.2rem;
    margin-bottom: 12px;
    display: inline-block;
    transition: all 0.4s ease;
}

.feature-box:hover .feature-icon {
    transform: scale(1.12) rotate(-5deg);
}

.feature-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a3a52;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.feature-desc {
    font-size: 0.85rem;
    color: #555;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

/* ════════════════════════════════════════════════════════════════ */
/* 📊 STAT BOX - LIGHT & COMPACT                                   */
/* ════════════════════════════════════════════════════════════════ */

.stat-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
    color: #1a3a52;
    padding: 24px;
    border-radius: 14px;
    text-align: center;
    border: 2px solid #e8ecf1;
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}

.stat-box:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 28px rgba(255, 215, 0, 0.15);
    border-color: #FFD700;
}

.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFD700, #00BCD4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.stat-label {
    font-size: 0.75rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 8px;
    font-weight: 600;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🔧 FILTER LABEL TEXT                                            */
/* ════════════════════════════════════════════════════════════════ */

.filter-label-text {
    font-size: 10px !important;
    font-weight: 700 !important;
    color: #1a3a52 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    margin-bottom: 10px !important;
    margin-top: 0 !important;
    display: block;
    background: linear-gradient(135deg, #FFD700, #00BCD4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🔧 SELECTBOX - LIGHT THEME                                     */
/* ════════════════════════════════════════════════════════════════ */

.stSelectbox {
    width: 100% !important;
}

.stSelectbox > div > div {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}

.stSelectbox:focus-within > div > div {
    border-color: #FFD700 !important;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1) !important;
}

.stSelectbox * {
    color: #1a3a52 !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] > div {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] [role="option"] {
    background: white !important;
    color: #1a3a52 !important;
}

div[data-baseweb="select"] [role="option"]:hover {
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(0, 188, 212, 0.1)) !important;
}

div[data-baseweb="select"] [role="option"][aria-selected="true"] {
    background: linear-gradient(135deg, #FFD700, #00BCD4) !important;
    color: #1a3a52 !important;
    font-weight: 700 !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🔧 TEXT INPUT - LIGHT                                          */
/* ════════════════════════════════════════════════════════════════ */

.stTextInput > div > div > input {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
    border-radius: 10px !important;
    color: #1a3a52 !important;
    font-weight: 500 !important;
    padding: 12px 14px !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #FFD700 !important;
    box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.1) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🔘 BUTTONS - INTERACTIVE                                       */
/* ════════════════════════════════════════════════════════════════ */

.stButton > button {
    background: linear-gradient(135deg, #1a3a52, #2a5a72) !important;
    color: white !important;
    border: 2px solid #1a3a52 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
    width: 100% !important;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #FFD700, #00BCD4) !important;
    color: #1a3a52 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 20px rgba(255, 215, 0, 0.25) !important;
    border-color: #FFD700 !important;
}

.stButton > button:active {
    transform: translateY(-1px) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* 📍 TIMELINE - LIGHT & COMPACT                                  */
/* ════════════════════════════════════════════════════════════════ */

.timeline-container {
    position: relative;
    padding: 50px 0 30px 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 18px;
    width: 100%;
}

.timeline-item {
    position: relative;
    display: flex;
    flex-direction: column;
}

.timeline-marker {
    position: absolute;
    left: 50%;
    top: -28px;
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #FFD700, #00BCD4);
    border: 3px solid white;
    border-radius: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.1rem;
    color: white;
    z-index: 10;
    box-shadow: 0 3px 12px rgba(255, 215, 0, 0.25);
    transition: all 0.3s ease;
}

.timeline-item:hover .timeline-marker {
    transform: translateX(-50%) scale(1.15);
    box-shadow: 0 6px 18px rgba(0, 188, 212, 0.3);
}

.timeline-content {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1.5px solid #e8ecf1;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    margin-top: 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
}

.timeline-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #FFD700, #00BCD4, #FF6B6B);
    background-size: 200% 100%;
}

.timeline-content:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 28px rgba(26, 58, 82, 0.12);
    border-color: #FFD700;
}

.timeline-label {
    font-size: 0.6rem;
    font-weight: 800;
    color: #00BCD4;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}

.timeline-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #1a3a52;
    margin: 0 0 6px 0;
    line-height: 1.3;
}

.timeline-desc {
    font-size: 0.72rem;
    color: #666;
    line-height: 1.4;
    margin: 0;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🎨 CTA SECTION                                                  */
/* ════════════════════════════════════════════════════════════════ */

.cta-section {
    background: linear-gradient(135deg, #1a3a52 0%, #2a5a72 50%, #1a4a5f 100%);
    color: white;
    padding: 48px 40px;
    border-radius: 14px;
    text-align: center;
    border: 2px solid #FFD700;
    position: relative;
    overflow: hidden;
}

.cta-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255, 215, 0, 0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.cta-section h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 12px;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}

/* ════════════════════════════════════════════════════════════════ */
/* 🔚 FOOTER                                                       */
/* ════════════════════════════════════════════════════════════════ */

.footer {
    background: linear-gradient(135deg, #1a3a52 0%, #2a5a72 100%);
    color: white;
    padding: 50px 40px;
    border-top: 3px solid;
    border-image: linear-gradient(90deg, #FFD700, #00BCD4) 1;
}

.footer-content {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 35px;
    margin-bottom: 28px;
}

.footer-section h3 {
    font-family: 'Playfair Display', serif;
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 14px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #FFD700, #00BCD4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.footer-section p, .footer-section a {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8);
    line-height: 1.7;
    margin: 0 0 10px 0;
    text-decoration: none;
    transition: all 0.3s ease;
}

.footer-section a:hover { 
    color: #FFD700;
    padding-left: 6px;
}

.footer-bottom {
    text-align: center;
    border-top: 1px solid rgba(255, 215, 0, 0.2);
    padding-top: 20px;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.6);
}

/* ════════════════════════════════════════════════════════════════ */
/* 📱 MOBILE RESPONSIVE                                            */
/* ════════════════════════════════════════════════════════════════ */

@media (max-width: 768px) {
    .header-gold-bar {
        flex-direction: column;
        gap: 12px;
        padding: 14px;
    }
    
    .hero-section { padding: 50px 20px; }
    .hero-title { font-size: 2rem; }
    .main-container { padding: 30px 16px; }
    .section-title { font-size: 1.4rem; }
    
    .feature-box {
        padding: 20px;
    }
    
    .timeline-container {
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 14px;
    }
}
</style>

<script>
function fixSelectboxColors() {
    const selects = document.querySelectorAll('[data-baseweb="select"]');
    selects.forEach((select) => {
        const allText = select.querySelectorAll('*');
        allText.forEach((el) => {
            if (el.textContent && el.textContent.trim()) {
                el.style.color = '#1a3a52';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', fixSelectboxColors);
setInterval(fixSelectboxColors, 500);
</script>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 SESSION STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🖼️ LOGO LOADING FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data
def load_logo_base64(logo_path):
    """Load logo dari local path dan convert ke base64"""
    try:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                img_data = img_file.read()
                b64_string = base64.b64encode(img_data).decode()
                return b64_string, True
        else:
            return None, False
    except Exception as e:
        st.warning(f"⚠️ Error loading logo: {e}")
        return None, False

# Load logo
logo_base64, logo_exists = load_logo_base64(LOGO_PATH)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔌 GOOGLE DRIVE FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_resource
def get_drive_service():
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)
    except:
        return None

def get_file_id(service, filename: str):
    if not service or not FOLDER_ID:
        return None
    try:
        results = service.files().list(
            q=f"name='{filename}' and '{FOLDER_ID}' in parents and trashed=false",
            fields="files(id, name)"
        ).execute()
        files = results.get("files", [])
        return files[0]["id"] if files else None
    except:
        return None

def download_from_drive(service, filename: str, dest_path: pathlib.Path) -> bool:
    if not service:
        return False
    try:
        file_id = get_file_id(service, filename)
        if not file_id:
            return False
        request = service.files().get_media(fileId=file_id)
        with open(dest_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return True
    except:
        return False

def upload_to_drive(service, local_path: pathlib.Path, filename: str):
    if not service or not FOLDER_ID:
        return
    try:
        file_id = get_file_id(service, filename)
        media = MediaFileUpload(str(local_path), mimetype="application/geo+json", resumable=True)
        if file_id:
            service.files().update(fileId=file_id, media_body=media).execute()
        else:
            metadata = {"name": filename, "parents": [FOLDER_ID]}
            service.files().create(body=metadata, media_body=media).execute()
    except:
        pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📂 DATA FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

drive_service = get_drive_service()

FILE_MAP = {
    "data tugas akhir.geojson": DATA_FILE,
    "Batas Administrasi Kabupaten Bandung.geojson": KABUPATEN_FILE,
    "Batas Administrasi Kecamatan Katapang.geojson": KECAMATAN_FILE,
    "RTRW.geojson": RTRW_FILE,
}

# ── LOAD FILES: PRIORITAS LOCAL PATH ──
# Cek data original dari local path dulu
if os.path.exists(LOCAL_DATA_PATH) and not DATA_FILE.exists():
    try:
        import shutil
        shutil.copy(LOCAL_DATA_PATH, DATA_FILE)
        st.success("✅ Data original loaded dari local path!")
    except Exception as e:
        st.warning(f"⚠️ Gagal copy data dari local: {e}")

# Jika local tidak ada atau gagal, coba download dari Google Drive
for fname, fpath in FILE_MAP.items():
    if not fpath.exists() and drive_service:
        download_from_drive(drive_service, fname, fpath)

@st.cache_data(ttl=0)
def load_data():
    """Load dan merge data original + uploaded data"""
    gdf_original = gpd.GeoDataFrame()
    gdf_uploaded = gpd.GeoDataFrame()
    
    # Load original data
    if DATA_FILE.exists():
        try:
            gdf_original = gpd.read_file(str(DATA_FILE))
            if gdf_original.crs is None:
                bounds = gdf_original.total_bounds
                gdf_original = gdf_original.set_crs("EPSG:3857" if abs(bounds[0]) > 180 else "EPSG:4326")
            if gdf_original.crs.to_epsg() != 4326:
                gdf_original = gdf_original.to_crs("EPSG:4326")
            if "OBJECTID" not in gdf_original.columns:
                gdf_original.insert(0, "OBJECTID", range(1, len(gdf_original) + 1))
            gdf_original["source"] = "original"  # Tag sebagai original
        except:
            pass
    
    # Load uploaded data
    if UPLOADED_DATA_FILE.exists():
        try:
            gdf_uploaded = gpd.read_file(str(UPLOADED_DATA_FILE))
            if gdf_uploaded.crs is None:
                gdf_uploaded = gdf_uploaded.set_crs("EPSG:4326")
            if gdf_uploaded.crs.to_epsg() != 4326:
                gdf_uploaded = gdf_uploaded.to_crs("EPSG:4326")
            if "OBJECTID" not in gdf_uploaded.columns:
                gdf_uploaded.insert(0, "OBJECTID", range(1, len(gdf_uploaded) + 1))
            gdf_uploaded["source"] = "uploaded"  # Tag sebagai uploaded
        except:
            pass
    
    # Merge
    if not gdf_original.empty and not gdf_uploaded.empty:
        gdf = gpd.GeoDataFrame(pd.concat([gdf_original, gdf_uploaded], ignore_index=True))
    elif not gdf_original.empty:
        gdf = gdf_original
    elif not gdf_uploaded.empty:
        gdf = gdf_uploaded
    else:
        gdf = gpd.GeoDataFrame()
    
    return gdf

@st.cache_data(ttl=0)
def load_boundary(filepath: str):
    try:
        gdf = gpd.read_file(filepath)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        return gdf
    except:
        return gpd.GeoDataFrame()

def save_data(gdf: gpd.GeoDataFrame, is_upload=False):
    """Save data ke file (original atau uploaded)"""
    try:
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        # Tentukan file tujuan
        target_file = UPLOADED_DATA_FILE if is_upload else DATA_FILE
        
        gdf.to_file(str(target_file), driver="GeoJSON")
        if drive_service and not is_upload:  # Hanya sync original ke drive
            upload_to_drive(drive_service, DATA_FILE, "data tugas akhir.geojson")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Error: {e}")

def read_shp_from_zip(uploaded_file):
    """Support multiple format: SHP (zip), KML, KMZ, GDB (zip)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simpan uploaded file
        temp_path = os.path.join(tmpdir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        
        # Handle berbagai format
        if uploaded_file.name.endswith('.zip'):
            # Extract ZIP dan cari SHP atau GDB
            with zipfile.ZipFile(temp_path, "r") as z:
                z.extractall(tmpdir)
            
            # Coba cari SHP dulu
            shp_files = list(Path(tmpdir).rglob("*.shp"))
            if shp_files:
                gdf = gpd.read_file(str(shp_files[0]))
            else:
                # Coba cari GDB (FileGeodatabase folder)
                gdb_files = list(Path(tmpdir).rglob("*.gdb"))
                if gdb_files:
                    gdf = gpd.read_file(str(gdb_files[0]))
                else:
                    raise ValueError("Tidak ada file .shp atau .gdb di dalam ZIP")
        
        elif uploaded_file.name.endswith('.kml'):
            # Baca KML langsung
            gdf = gpd.read_file(temp_path, driver='KML')
        
        elif uploaded_file.name.endswith('.kmz'):
            # KMZ adalah ZIP berisi KML
            with zipfile.ZipFile(temp_path, "r") as z:
                z.extractall(tmpdir)
            kml_files = list(Path(tmpdir).rglob("*.kml"))
            if kml_files:
                gdf = gpd.read_file(str(kml_files[0]), driver='KML')
            else:
                raise ValueError("Tidak ada file .kml di dalam KMZ")
        
        elif uploaded_file.name.endswith('.gdb'):
            # GDB sebagai file langsung tidak bisa, harus dalam ZIP
            raise ValueError("❌ GDB harus di-compress dalam ZIP terlebih dahulu (.zip)")
        
        else:
            raise ValueError(f"Format {uploaded_file.name} tidak didukung. Gunakan: SHP (ZIP), KML, KMZ, GDB (ZIP)")
        
        # Normalize CRS
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        if "OBJECTID" not in gdf.columns:
            gdf.insert(0, "OBJECTID", range(1, len(gdf) + 1))
        
        return gdf

def center_map(gdf):
    try:
        c = gdf.geometry.unary_union.centroid
        return [c.y, c.x], 15
    except:
        return [-6.99, 107.55], 13

def display_cols(df):
    return [c for c in df.columns if c != "geometry"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 LOAD DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

gdf = load_data()
gdf_kabupaten = load_boundary(str(KABUPATEN_FILE)) if KABUPATEN_FILE.exists() else None
gdf_kecamatan = load_boundary(str(KECAMATAN_FILE)) if KECAMATAN_FILE.exists() else None
gdf_rtrw = load_boundary(str(RTRW_FILE)) if RTRW_FILE.exists() else None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 HEADER WITH LOGO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if logo_exists and logo_base64:
    header_html = f"""
    <div class="header-gold-bar">
        <div class="header-left">
            <img src="data:image/png;base64,{logo_base64}" class="header-logo-img" alt="Logo">
        </div>
    """
else:
    header_html = f"""
    <div class="header-gold-bar">
        <div class="header-left">
            <div class="header-logo-placeholder">🗺️</div>
        </div>
    """

if logo_exists and logo_base64:
    header_html = f"""
    <div class="header-gold-bar">
        <div class="header-left">
            <img src="data:image/png;base64,{logo_base64}" class="header-logo-img" alt="Logo">
        </div>
    """
else:
    header_html = f"""
    <div class="header-gold-bar">
        <div class="header-left">
            <div class="header-logo-placeholder">🗺️</div>
        </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗺️ PETA", use_container_width=True, key="nav1"):
        st.session_state.current_page = "peta"
        st.rerun()
with col2:
    if st.button("📋 TENTANG PLATFORM", use_container_width=True, key="nav2"):
        st.session_state.current_page = "beranda"
        st.rerun()
with col3:
    if st.button("🔐 ADMIN", use_container_width=True, key="nav3"):
        st.session_state.current_page = "admin"
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

if not logo_exists:
    st.warning(f"⚠️ Logo tidak ditemukan di: {LOGO_PATH}\n\nGunakan emoji placeholder. Untuk ganti logo, update LOGO_PATH di kode.")

# ════════════════════════════════════════════════════════════════════════════
# 📍 PAGE: LANDING
# ════════════════════════════════════════════════════════════════════════════

if st.session_state.current_page == "landing":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-icon">🗺️</div>
            <h1 class="hero-title">Solusi Geospasial Terdepan</h1>
            <p class="hero-subtitle">
                Platform interaktif untuk manajemen dan publikasi data rekomendasi teknis pemanfaatan ruang. 
                Dengan teknologi terkini, kami memudahkan visualisasi, analisis, dan pengelolaan data geospasial Anda.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">✨ Fitur Unggulan</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🗺️</div>
            <h3 class="feature-title">Visualisasi Interaktif</h3>
            <p class="feature-desc">Tampilkan data dengan peta interaktif, multi-layer, dan filter advanced untuk analisis mendalam.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📤</div>
            <h3 class="feature-title">Upload Shapefile</h3>
            <p class="feature-desc">Unggah data SHP dengan mudah dan otomatis tersinkronisasi ke cloud.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔐</div>
            <h3 class="feature-title">Admin Dashboard</h3>
            <p class="feature-desc">Kelola data dengan aman di dashboard terproteksi dengan fitur lengkap.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 Database Kami</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><p class="stat-number">{len(gdf)}</p><p class="stat-label">📍 Total Data</p></div>', unsafe_allow_html=True)
    with col2:
        n = gdf["PEMANFAATAN RUANG"].nunique() if "PEMANFAATAN RUANG" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><p class="stat-number">{n}</p><p class="stat-label">🏙️ Pemanfaatan</p></div>', unsafe_allow_html=True)
    with col3:
        n = gdf["PERATURAN ZONASI"].nunique() if "PERATURAN ZONASI" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><p class="stat-number">{n}</p><p class="stat-label">📋 Zonasi</p></div>', unsafe_allow_html=True)
    with col4:
        n = gdf["TAHUN"].nunique() if "TAHUN" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><p class="stat-number">{n}</p><p class="stat-label">📅 Tahun</p></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cta-section">
        <h2>Siap Menggunakan WebGIS?</h2>
        <p>Jelajahi peta interaktif, kelola data dengan mudah, dan optimalkan pengambilan keputusan berbasis data geospasial.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == "beranda":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">Tentang Platform</h1>
            <p class="hero-subtitle">Solusi Geospasial Terdepan untuk Pemanfaatan Ruang</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # INTRO SECTION
    # ════════════════════════════════════════════════════════════════
    
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 30px; border-radius: 12px; border-left: 5px solid #D4AF37;">
            <h3 style="color: #1a2744; font-weight: 700; font-size: 1.3rem; margin-top: 0;">📋 Tentang Platform</h3>
            <p style="color: #555; line-height: 1.8; font-size: 0.95rem;">
                Sistem ini dirancang untuk mendukung pengelolaaan <span style="font-weight: 600; color: #1a2744;">Rekomendasi Teknis Pemanfaatan Ruang</span> secara lebih cepat, tertib, dan transparan.
            </p>
            <p style="color: #888; font-size: 0.9rem; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
                ✅ Akurat | ✅ Terpercaya | ✅ Terintegrasi
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # FITUR UTAMA
        st.markdown("""
        <div style="background: #ffffff; padding: 0;">
            <h3 style="color: #1a2744; font-weight: 700; font-size: 1.2rem; margin-bottom: 20px;">🎯 Fitur Utama</h3>
        </div>
        """, unsafe_allow_html=True)
        
        features = [
            ("🗺️", "Visualisasi Peta Interaktif", "Tampilkan polygon pemanfaatan ruang di atas basemap dengan klik-info detail."),
            ("📤", "Upload & Manajemen Data SHP", "Admin dapat mengunggah shapefile (.zip) untuk memperbaharui layer spatial."),
            ("🔍", "Filter & Pencarian Data", "Filter berdasarkan tahun, jenis pemanfaatan, atau peraturan zonasi."),
            ("🏗️", "Layer RTRW Terintegrasi", "Overlay data RTRW pada peta untuk analisis kesesuaian pemanfaatan ruang."),
            ("🔐", "Akses Admin Terproteksi", "Dashboard admin dilindungi password — hanya pengelola yang dapat mengedit data."),
        ]
        
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #D4AF37;">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 24px;">{icon}</span>
                    <div>
                        <p style="margin: 0; font-weight: 600; color: #1a2744; font-size: 0.95rem;">{title}</p>
                        <p style="margin: 4px 0 0 0; color: #666; font-size: 0.85rem; line-height: 1.5;">{desc}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div style="background: #ffffff; padding: 0;">
            <h3 style="color: #1a2744; font-weight: 700; font-size: 1.2rem; margin-bottom: 20px;">🏗️ Jenis Pemanfaatan Ruang</h3>
        </div>
        """, unsafe_allow_html=True)
        
        pemanfaatan_jenis = [
            ("🏠", "Kawasan Permukiman", "Area peruntukan hunian perkotaan maupun perdesaan."),
            ("🛍️", "Kawasan Perdagangan & Jasa", "Pusat perbelanjaan, ruko, pasar, perkantoran swasta."),
            ("🌳", "Ruang Terbuka Hijau", "Taman kota, hutan kota, jalur hijau, sempadan sungai."),
            ("🏭", "Kawasan Industri", "Area industri besar, sedang, maupun rumah tangga."),
            ("🌾", "Kawasan Pertanian & Lahan Khusus", "Lahan pertanian pangan berkelanjutan dan kawasan lindung."),
        ]
        
        for icon, title, desc in pemanfaatan_jenis:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #e07b39;">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 24px;">{icon}</span>
                    <div>
                        <p style="margin: 0; font-weight: 600; color: #1a2744; font-size: 0.95rem;">{title}</p>
                        <p style="margin: 4px 0 0 0; color: #666; font-size: 0.85rem; line-height: 1.5;">{desc}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # STATS SECTION
    # ════════════════════════════════════════════════════════════════
    
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 Database Kami</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><p class="stat-number">{len(gdf)}</p><p class="stat-label">📍 Total Data</p></div>', unsafe_allow_html=True)
    with col2:
        n = gdf["PEMANFAATAN RUANG"].nunique() if "PEMANFAATAN RUANG" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><p class="stat-number">{n}</p><p class="stat-label">🏙️ Pemanfaatan</p></div>', unsafe_allow_html=True)
    with col3:
        n = gdf["PERATURAN ZONASI"].nunique() if "PERATURAN ZONASI" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><p class="stat-number">{n}</p><p class="stat-label">📋 Zonasi</p></div>', unsafe_allow_html=True)
    with col4:
        n = gdf["TAHUN"].nunique() if "TAHUN" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><p class="stat-number">{n}</p><p class="stat-label">📅 Tahun</p></div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # TIMELINE SECTION
    # ════════════════════════════════════════════════════════════════
    
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📍 Alur Rekomendasi Teknis Pemanfaatan Ruang</h2>
    </div>
    """, unsafe_allow_html=True)

    # Build timeline HTML
    timeline_html = '<div class="timeline-container">'
    
    timeline_data = [
        ("1", "Pelaku Usaha Membuat NIB melalui OSS", "Permohonan Nomor Induk Berusaha melalui portal oss.go.id"),
        ("2", "Pendaftaran & Melengkapi Dokumen", "Registrasi permohonan dan melengkapi seluruh dokumen yang dipersyaratkan"),
        ("3", "Diproses Oleh Sekretariat & Disposisi Kepala Dinas", "Persyaratan diterima oleh sekretaris dan diberikan disposisi kepada kepala dinas"),
        ("4", "Disposisi Bidang Tata Ruang", "Kepala Dinas memberikan disposisi kepada Bidang Tata Ruang untuk ditindaklanjuti"),
        ("5", "Survei / Verifikasi Berkas", "Survey lapangan luas diatas 1000m² - Verifikasi berkas luas kurang dari 1000m²"),
        ("6", "Pengobahan Berkas", "Berkas diproses dan diolah sesuai teknis Bidang Tata Ruang"),
        ("7", "Proses Revisi & Persetujuan", "Draft rekomendasi direvisi dan dimintakan persetujuan internal"),
        ("8", "Verifikasi oleh Kepala Bidang Tata Ruang", "Kepala Bidang melakukan telaah dan memberikan persetujuan"),
        ("9", "Proses ITD Kepala Bidang / Kepala Dinas", "Surat ditandatangani oleh Kepala Bidang atau Kepala Dinas sesuai kewenangan"),
        ("10", "Registrasi Surat", "Surat rekomendasi teknis distribusi nomor registrasi dalam data sekretariat"),
        ("11", "Pengambilan Produk", "Permohonan mengambil surat rekomendasi teknis yang telah ditandatangani"),
    ]
    
    for num, title, desc in timeline_data:
        timeline_html += f'<div class="timeline-item"><div class="timeline-marker">{num}</div><div class="timeline-content"><div class="timeline-label">Langkah {num}</div><div class="timeline-title">{title}</div><div class="timeline-desc">{desc}</div></div></div>'
    
    timeline_html += '</div>'
    
    st.markdown(timeline_html, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == "peta":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">Peta Publik Pemanfaatan Ruang</h1>
            <p class="hero-subtitle">Visualisasi data geospasial dengan filter advanced</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # ── PREPARE FILTER OPTIONS ──
    tahun_opts = ["Semua"] + sorted(gdf["TAHUN"].dropna().astype(str).unique().tolist()) if "TAHUN" in gdf.columns else ["Semua"]
    pmnft_opts = ["Semua"] + sorted(gdf["PEMANFAATAN RUANG"].dropna().astype(str).unique().tolist()) if "PEMANFAATAN RUANG" in gdf.columns else ["Semua"]
    zona_opts = ["Semua"] + sorted(gdf["PERATURAN ZONASI"].dropna().astype(str).unique().tolist()) if "PERATURAN ZONASI" in gdf.columns else ["Semua"]

    # ── RENDER FILTER ──
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write('<p class="filter-label-text">📅 TAHUN</p>', unsafe_allow_html=True)
        f_tahun = st.selectbox("Tahun", tahun_opts, label_visibility="collapsed", key="tahun_filter")
    
    with col2:
        st.write('<p class="filter-label-text">🏙️ PEMANFAATAN</p>', unsafe_allow_html=True)
        f_pmnft = st.selectbox("Pemanfaatan", pmnft_opts, label_visibility="collapsed", key="pmnft_filter")
    
    with col3:
        st.write('<p class="filter-label-text">📋 ZONASI</p>', unsafe_allow_html=True)
        f_zona = st.selectbox("Zonasi", zona_opts, label_visibility="collapsed", key="zona_filter")
    
    with col4:
        st.write('<p class="filter-label-text">🔍 CARI</p>', unsafe_allow_html=True)
        f_kw = st.text_input("Cari Keyword", label_visibility="collapsed", placeholder="Keyword...", key="search_filter")

    # ── APPLY FILTERS ──
    fgdf = gdf.copy()
    is_filtered = False  # Track apakah ada filter aktif
    
    if f_tahun != "Semua": 
        fgdf = fgdf[fgdf["TAHUN"].astype(str) == f_tahun]
        is_filtered = True
    if f_pmnft != "Semua": 
        fgdf = fgdf[fgdf["PEMANFAATAN RUANG"].astype(str) == f_pmnft]
        is_filtered = True
    if f_zona != "Semua": 
        fgdf = fgdf[fgdf["PERATURAN ZONASI"].astype(str) == f_zona]
        is_filtered = True
    if f_kw:
        mask = pd.Series(False, index=fgdf.index)
        for col in ["REMARK", "KODEKBLI"]:
            if col in fgdf.columns:
                mask |= fgdf[col].astype(str).str.contains(f_kw, case=False, na=False)
        fgdf = fgdf[mask]
        is_filtered = True

    st.caption(f"📊 Menampilkan **{len(fgdf)}** dari **{len(gdf)}** data")
    
    if is_filtered:
        st.info("🔍 **Filter Aktif:** Layer RTRW dinonaktifkan | Data hasil filter di-highlight KUNING")

    # ── RENDER MAP ──
    with st.spinner("⏳ Memuat peta…"):
        center, zoom = center_map(fgdf if not fgdf.empty else gdf)
        m = leafmap.Map(center=center, zoom=zoom, height=500)
        m.add_basemap("OpenStreetMap")
        
        if gdf_kabupaten is not None and not gdf_kabupaten.empty:
            m.add_gdf(gdf_kabupaten, layer_name="Batas Kab. Bandung",
                style={"color":"#2d6a4f","fillColor":"#2d6a4f","fillOpacity":0.04,"weight":2.0},
                info_mode="on_hover")
        
        if gdf_kecamatan is not None and not gdf_kecamatan.empty:
            m.add_gdf(gdf_kecamatan, layer_name="Batas Kec. Katapang",
                style={"color":"#e07b39","fillColor":"#e07b39","fillOpacity":0.06,"weight":2.5},
                info_mode="on_hover")
        
        # RTRW layer HANYA tampil jika TIDAK ada filter aktif
        if not is_filtered:
            if gdf_rtrw is not None and not gdf_rtrw.empty:
                m.add_gdf(gdf_rtrw, layer_name="🏗️ RTRW",
                    style={"color":"#ff6b6b","fillColor":"#ff6b6b","fillOpacity":0.08,"weight":2.0},
                    info_mode="on_hover")
        
        # Data hasil filter dengan HIGHLIGHT KUNING
        if not fgdf.empty:
            if is_filtered:
                # Jika ada filter: highlight kuning
                m.add_gdf(fgdf, layer_name="✨ Hasil Filter (Highlight)",
                    style={"color":"#FFD700","fillColor":"#FFD700","fillOpacity":0.55,"weight":2.5},
                    info_mode="on_click")
            else:
                # Jika tidak ada filter: warna normal navy/gold
                m.add_gdf(fgdf, layer_name="Pemanfaatan Ruang",
                    style={"color":"#1a3a52","fillColor":"#FFD700","fillOpacity":0.35,"weight":1.5},
                    info_mode="on_click")
        
        # Data yang tidak ter-filter dengan warna GRAY TRANSPARAN (hanya jika ada filter)
        if is_filtered and not gdf.empty:
            non_filtered = gdf[~gdf.index.isin(fgdf.index)]
            if not non_filtered.empty:
                m.add_gdf(non_filtered, layer_name="Data Lainnya (Redup)",
                    style={"color":"#999999","fillColor":"#999999","fillOpacity":0.12,"weight":0.5},
                    info_mode="on_hover")
        
        # ── ADD LEGEND ──
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 10px;
                    background-color: white; border:2px solid #1a3a52; 
                    z-index:9999; font-size:13px;
                    padding: 10px 14px; border-radius: 8px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                    width: auto; white-space: nowrap;">
            
            <div style="font-weight: bold; margin-bottom: 8px; color: #1a3a52; font-size: 13px;">
                📍 LEGENDA
            </div>
        '''
        
        if is_filtered:
            # Legenda ketika ada filter aktif
            legend_html += '''
            <div style="margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FFD700; border: 1.5px solid #FFC700; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="color: #1a3a52; font-weight: 500;">Hasil Filter</span>
                </div>
            </div>
            
            <div style="margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #d0d0d0; border: 1.5px solid #999999; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="color: #1a3a52; font-weight: 500;">Data Lainnya</span>
                </div>
            </div>
            '''
        else:
            # Legenda ketika tidak ada filter
            legend_html += '''
            <div style="margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FFD700; border: 1.5px solid #1a3a52; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="color: #1a3a52; font-weight: 500;">Pemanfaatan Ruang</span>
                </div>
            </div>
            
            <div style="margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FF6B6B; border: 1.5px solid #FF4444; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="color: #1a3a52; font-weight: 500;">Layer RTRW</span>
                </div>
            </div>
            '''
        
        legend_html += '''
            <div style="margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FF9800; border: 1.5px solid #F57C00; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="color: #1a3a52; font-weight: 500;">Batas Kecamatan</span>
                </div>
            </div>
            
            <div style="margin-bottom: 0px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #4CAF50; border: 1.5px solid #388E3C; border-radius: 2px; flex-shrink: 0;"></div>
                    <span style="color: #1a3a52; font-weight: 500;">Batas Kabupaten</span>
                </div>
            </div>
            
            <div style="border-top: 1px solid #e0e0e0; margin-top: 8px; padding-top: 8px; font-size: 11px; color: #666;">
                ⚡ Klik polygon untuk info
            </div>
        </div>
        '''
        
        m.add_html(legend_html)
    
    try:
        m.to_streamlit(height=500)
    except Exception as e:
        # Fallback: render peta sebagai HTML jika to_streamlit error
        try:
            components.html(m._repr_html_(), height=500)
        except:
            st.error("⚠️ Gagal memuat peta. Silakan refresh halaman.")

    # ── DATA TABLE ──
    st.markdown('<div class="map-section">', unsafe_allow_html=True)
    if fgdf.empty:
        st.warning("⚠️ Tidak ada data")
    else:
        st.dataframe(fgdf[display_cols(fgdf)], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == "admin":
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">Admin Panel</h1>
            <p class="hero-subtitle">Kelola data pemanfaatan ruang dengan aman</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        st.warning("🔒 Silakan login")
        with st.form("login"):
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Password salah")
    else:
        st.success("✅ Login sebagai Admin")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Upload Data Baru", "✏️ Edit", "🗑️ Hapus", "📥 Export", "🔧 Restore Original"])
        
        with tab1:
            st.subheader("📤 Upload Data Geospasial")
            
            st.markdown("""
            <div style="background: #f0f2f5; padding: 12px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 16px;">
                <p style="margin: 0; font-size: 0.9rem; color: #1a3a52;">
                    <strong>Format yang didukung:</strong><br>
                    🔹 <strong>SHP</strong> → ZIP berisi .shp, .shx, .dbf, dll<br>
                    🔹 <strong>KML</strong> → File KML langsung<br>
                    🔹 <strong>KMZ</strong> → ZIP berisi KML<br>
                    🔹 <strong>GDB</strong> → ZIP berisi FileGeodatabase
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Pilih file untuk upload",
                type=["zip", "kml", "kmz", "gdb"],
                help="Drag & drop atau klik untuk pilih file"
            )
            
            if uploaded_file:
                try:
                    st.info(f"📁 File: {uploaded_file.name}")
                    shp = read_shp_from_zip(uploaded_file)
                    
                    st.success(f"✅ File berhasil dibaca! ({len(shp)} features)")
                    st.markdown("**Preview Data:**")
                    st.dataframe(shp[display_cols(shp)].head(5), use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Simpan ke Database", use_container_width=True, type="primary"):
                            save_data(shp, is_upload=True)  # SAVE KE UPLOADED FILE!
                            st.success("✅ Data berhasil tersimpan!")
                    with col2:
                        if st.button("❌ Batal", use_container_width=True):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Pastikan format file benar dan sesuai dengan standar geospasial.")
        
        with tab2:
            st.subheader("✏️ Edit Data Uploaded")
            
            # Load uploaded data saja
            gdf_uploaded = gpd.GeoDataFrame()
            if UPLOADED_DATA_FILE.exists():
                try:
                    gdf_uploaded = gpd.read_file(str(UPLOADED_DATA_FILE))
                except:
                    pass
            
            if gdf_uploaded.empty:
                st.info("📭 Tidak ada data uploaded")
            else:
                st.caption(f"📊 Menampilkan {len(gdf_uploaded)} data yang di-upload")
                st.dataframe(gdf_uploaded[display_cols(gdf_uploaded)], use_container_width=True, height=300)
                st.info("💡 Edit data bisa dilakukan di sini. Fitur edit detail akan ditambahkan.")
        
        with tab3:
            st.subheader("🗑️ Hapus Data Uploaded")
            
            # Load uploaded data saja
            gdf_uploaded = gpd.GeoDataFrame()
            if UPLOADED_DATA_FILE.exists():
                try:
                    gdf_uploaded = gpd.read_file(str(UPLOADED_DATA_FILE))
                except:
                    pass
            
            if gdf_uploaded.empty:
                st.info("📭 Tidak ada data uploaded untuk dihapus")
            else:
                st.warning("⚠️ Hapus akan menghapus 1 polygon saja, data original tetap aman!")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    id_to_delete = st.selectbox(
                        "Pilih polygon untuk dihapus",
                        gdf_uploaded["OBJECTID"].tolist(),
                        format_func=lambda x: f"ID {x}"
                    )
                with col2:
                    st.write("")  # spacing
                    st.write("")  # spacing
                
                # Tampilkan detail polygon yang akan dihapus
                if id_to_delete:
                    polygon_to_delete = gdf_uploaded[gdf_uploaded["OBJECTID"] == id_to_delete].iloc[0]
                    st.markdown("**Detail Polygon yang akan dihapus:**")
                    detail_dict = {k: v for k, v in polygon_to_delete.items() if k != "geometry"}
                    st.json(detail_dict)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🗑️ HAPUS POLYGON", use_container_width=True, type="secondary"):
                        # Hapus hanya polygon tertentu
                        gdf_updated = gdf_uploaded[gdf_uploaded["OBJECTID"] != id_to_delete].copy()
                        save_data(gdf_updated, is_upload=True)
                        st.success(f"✅ Polygon ID {id_to_delete} berhasil dihapus!")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ HAPUS SEMUA DATA UPLOADED", use_container_width=True, type="secondary"):
                        if UPLOADED_DATA_FILE.exists():
                            UPLOADED_DATA_FILE.unlink()
                        st.success("✅ Semua data uploaded berhasil dihapus!")
                        st.rerun()
                
                with col3:
                    pass
        
        with tab5:
            st.subheader("🔧 Restore Data Original")
            
            st.markdown("""
            <div style="background: #fff3cd; padding: 14px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 16px;">
                <p style="margin: 0; font-size: 0.9rem; color: #856404;">
                    <strong>⚠️ Gunakan tab ini untuk restore/upload data original Pemanfaatan Ruang.</strong><br>
                    Data akan disimpan terpisah dan TIDAK akan terhapus ketika menghapus data uploaded.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            original_file = st.file_uploader(
                "Upload Data Original (GeoJSON)",
                type=["geojson"],
                help="Upload file .geojson yang berisi data original pemanfaatan ruang"
            )
            
            if original_file:
                try:
                    st.info(f"📁 File: {original_file.name}")
                    
                    # Read file
                    original_gdf = gpd.read_file(original_file)
                    
                    # Normalize CRS
                    if original_gdf.crs is None:
                        original_gdf = original_gdf.set_crs("EPSG:4326")
                    elif original_gdf.crs.to_epsg() != 4326:
                        original_gdf = original_gdf.to_crs("EPSG:4326")
                    
                    # Add OBJECTID if not exists
                    if "OBJECTID" not in original_gdf.columns:
                        original_gdf.insert(0, "OBJECTID", range(1, len(original_gdf) + 1))
                    
                    st.success(f"✅ File berhasil dibaca! ({len(original_gdf)} features)")
                    st.markdown("**Preview Data Original:**")
                    st.dataframe(original_gdf[display_cols(original_gdf)].head(5), use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Simpan Sebagai DATA ORIGINAL", use_container_width=True, type="primary"):
                            # Save ke DATA_FILE (original file)
                            save_data(original_gdf, is_upload=False)
                            st.success("✅ Data original berhasil di-restore!")
                            st.balloons()
                            st.rerun()
                    with col2:
                        if st.button("❌ Batal", use_container_width=True):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Pastikan file adalah valid GeoJSON dengan extension .geojson")
            
            st.divider()
            
            st.markdown("**📊 Status Data Original Saat Ini:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if DATA_FILE.exists():
                    try:
                        gdf_original = gpd.read_file(str(DATA_FILE))
                        st.success(f"✅ Ada: {len(gdf_original)} polygons")
                        st.markdown("**Columns:**")
                        st.write(", ".join(display_cols(gdf_original)))
                    except:
                        st.warning("⚠️ File corrupted atau format error")
                else:
                    st.warning("📭 Belum ada data original")
            
            with col2:
                if UPLOADED_DATA_FILE.exists():
                    try:
                        gdf_up = gpd.read_file(str(UPLOADED_DATA_FILE))
                        st.info(f"📤 Data Uploaded: {len(gdf_up)} polygons")
                    except:
                        st.info("📭 Data Uploaded: Empty")
                else:
                    st.info("📭 Data Uploaded: Empty")
        
        with tab4:
            st.subheader("📥 Export Data")
            
            exp_col1, exp_col2 = st.columns(2)
            
            with exp_col1:
                st.write("**📍 Data Original (Pemanfaatan Ruang)**")
                if DATA_FILE.exists() and not gdf.empty:
                    gdf_original_only = gdf[gdf.get("source") == "original"]
                    if not gdf_original_only.empty:
                        st.download_button(
                            "📥 Download Original",
                            gdf_original_only.drop(columns=["source"], errors="ignore").to_json(),
                            "data_original.geojson",
                            "application/geo+json",
                            use_container_width=True
                        )
                    else:
                        st.info("📭 Tidak ada data original")
                else:
                    st.info("📭 Tidak ada data original")
            
            with exp_col2:
                st.write("**📤 Data Uploaded**")
                if UPLOADED_DATA_FILE.exists():
                    try:
                        gdf_uploaded = gpd.read_file(str(UPLOADED_DATA_FILE))
                        st.download_button(
                            "📥 Download Uploaded",
                            gdf_uploaded.drop(columns=["source"], errors="ignore").to_json(),
                            "data_uploaded.geojson",
                            "application/geo+json",
                            use_container_width=True
                        )
                    except:
                        st.info("📭 Tidak ada data uploaded")
                else:
                    st.info("📭 Tidak ada data uploaded")
            
            st.divider()
            
            st.write("**📦 Download Semua Data (Merged)**")
            if not gdf.empty:
                st.download_button(
                    "📥 Download Semua Data",
                    gdf.drop(columns=["source"], errors="ignore").to_json(),
                    "data_all.geojson",
                    "application/geo+json",
                    use_container_width=True,
                    type="primary"
                )

    st.markdown('</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 🔚 FOOTER
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="footer">
    <div class="footer-content">
        <div class="footer-section">
            <h3>🏢 Tentang</h3>
            <p>WebGIS Pemanfaatan Ruang adalah platform interaktif untuk manajemen data geospasial, dikembangkan oleh Universitas Pendidikan Indonesia (UPI).</p>
        </div>
        <div class="footer-section">
            <h3>🔗 Link</h3>
            <a href="https://upi.edu">UPI Official</a><br>
            <a href="#">Data Geospasial</a><br>
            <a href="#">Dokumentasi</a>
        </div>
        <div class="footer-section">
            <h3>📞 Kontak</h3>
            <p>Email: gis@upi.edu<br>Telepon: (022) XXXX-XXXX</p>
        </div>
    </div>
    <div class="footer-bottom">
        © 2026 WebGIS Pemanfaatan Ruang — Universitas Pendidikan Indonesia
    </div>
</div>
""", unsafe_allow_html=True)
