"""
🗺️ WebGIS Pemanfaatan Ruang - DATA UTAMA LANGSUNG MUNCUL
Data utama otomatis di-load dari file
Admin panel hanya untuk data TAMBAHAN
✅ FIXED: Nama file sekarang flexible
"""

import os
import io
import time
import base64
import zipfile
import tempfile
import pathlib
from pathlib import Path

import geopandas as gpd
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import leafmap.foliumap as leafmap

from PIL import Image

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📁 DATA PATHS
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ✅ FIXED: Flexible file naming - cek semua kemungkinan nama file
def find_geojson_file(directory, patterns):
    """Cari file geojson dengan berbagai kemungkinan nama"""
    for pattern in patterns:
        files = list(Path(directory).glob(pattern))
        if files:
            return files[0]
    return None

# Data utama - cek berbagai nama
DATA_FILE = find_geojson_file(DATA_DIR, [
    "DATA_PEMANFAATAN.geojson",
    "data_pemanfaatan.geojson",
    "DATA*.geojson"
])

# Batas Kabupaten - cek berbagai nama
KABUPATEN_FILE = find_geojson_file(DATA_DIR, [
    "Batas_Kabupaten.geojson",
    "batas_kabupaten.geojson",
    "*Kabupaten*.geojson",
    "*kabupaten*.geojson"
])

# Batas Kecamatan - cek berbagai nama
KECAMATAN_FILE = find_geojson_file(DATA_DIR, [
    "Batas_Kecamatan.geojson",
    "batas_kecamatan.geojson",
    "*Kecamatan*.geojson",
    "*kecamatan*.geojson"
])

# RTRW - cek berbagai nama
RTRW_FILE = find_geojson_file(DATA_DIR, [
    "RTRW.geojson",
    "rtrw.geojson",
    "*RTRW*.geojson",
    "*rtrw*.geojson"
])

# File data TAMBAHAN dari admin upload (terpisah di temp)
TEMP_DIR = pathlib.Path(tempfile.gettempdir()) / "webgis_additional"
TEMP_DIR.mkdir(exist_ok=True)
ADDITIONAL_DATA_FILE = TEMP_DIR / "data_additional.geojson"

# 🖼️ LOGO
LOGO_PATH = r"logoupimerah.png"

# 🔐 ADMIN PASSWORD
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")

st.set_page_config(
    page_title="WebGIS Pemanfaatan Ruang",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 CSS STYLING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --navy: #1a3a52;
    --gold: #FFD700;
    --teal: #00BCD4;
    --coral: #FF6B6B;
}

* { box-sizing: border-box; }
html, body { 
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important;
}

.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%) !important; }

.header-gold-bar {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
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
}

.header-logo-img {
    max-width: 65px;
    height: auto;
    max-height: 65px;
    object-fit: contain;
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
}

.stButton > button {
    background: linear-gradient(135deg, #1a3a52, #2a5a72) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #FFD700, #FFC700) !important;
    color: #1a3a52 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 20px rgba(255, 215, 0, 0.3) !important;
}

.hero-section {
    background: linear-gradient(135deg, #1a3a52 0%, #2a5a72 100%);
    color: white;
    padding: 60px 40px;
    text-align: center;
    border-radius: 12px;
    margin-bottom: 30px;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    text-transform: uppercase;
}

.hero-subtitle {
    font-size: 1rem;
    opacity: 0.9;
    margin-top: 12px;
    color: #00BCD4;
}

.feature-box {
    background: white;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    border: 1.5px solid #e8ecf1;
    transition: all 0.3s ease;
}

.feature-box:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(26, 58, 82, 0.12);
    border-color: #FFD700;
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.feature-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a3a52;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.feature-desc {
    font-size: 0.85rem;
    color: #666;
    line-height: 1.5;
}

.stat-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
    color: #1a3a52;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    border: 2px solid #e8ecf1;
}

.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
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
    font-weight: 600;
    margin-top: 8px;
}

.filter-label {
    font-size: 10px !important;
    font-weight: 700 !important;
    color: #1a3a52 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    margin-bottom: 8px !important;
}

.stSelectbox > div > div {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
    border-radius: 10px !important;
}

.stSelectbox * {
    color: #1a3a52 !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] > div {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
}

div[data-baseweb="select"] [role="option"] {
    background: white !important;
    color: #1a3a52 !important;
}

.footer {
    background: linear-gradient(135deg, #1a3a52 0%, #2a5a72 100%);
    color: white;
    padding: 40px;
    border-radius: 12px;
    margin-top: 50px;
    text-align: center;
    font-size: 0.85rem;
}

@media (max-width: 768px) {
    .hero-title { font-size: 1.8rem; }
    .header-gold-bar { flex-direction: column; gap: 12px; }
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
# 🖼️ LOGO LOADING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data
def load_logo_base64(logo_path):
    try:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                img_data = img_file.read()
                b64_string = base64.b64encode(img_data).decode()
                return b64_string, True
        return None, False
    except:
        return None, False

logo_base64, logo_exists = load_logo_base64(LOGO_PATH)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📂 DATA LOADING FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def load_boundary(filepath):
    """Load boundary data"""
    try:
        if filepath is None or not os.path.exists(str(filepath)):
            return gpd.GeoDataFrame()
        
        gdf = gpd.read_file(str(filepath))
        if gdf.empty:
            return gpd.GeoDataFrame()
        
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        return gdf
    except Exception as e:
        st.warning(f"⚠️ Tidak bisa load file: {filepath}")
        return gpd.GeoDataFrame()

def load_main_data():
    """
    LOAD DATA UTAMA - Langsung dari file, tidak perlu admin upload
    Ini adalah database utama yang selalu ada
    """
    try:
        if DATA_FILE is None or not DATA_FILE.exists():
            return gpd.GeoDataFrame()
        
        gdf = gpd.read_file(str(DATA_FILE))
        
        if gdf.empty:
            return gpd.GeoDataFrame()
        
        # Normalize CRS
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        # Add OBJECTID
        if "OBJECTID" not in gdf.columns:
            gdf.insert(0, "OBJECTID", range(1, len(gdf) + 1))
        
        gdf["source"] = "main"  # Tag sebagai main data
        return gdf
        
    except Exception as e:
        st.error(f"❌ Error load data utama: {str(e)}")
        return gpd.GeoDataFrame()

def load_additional_data():
    """
    LOAD DATA TAMBAHAN - Dari upload admin
    """
    try:
        if not ADDITIONAL_DATA_FILE.exists():
            return gpd.GeoDataFrame()
        
        gdf = gpd.read_file(str(ADDITIONAL_DATA_FILE))
        
        if gdf.empty:
            return gpd.GeoDataFrame()
        
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        if "OBJECTID" not in gdf.columns:
            gdf.insert(0, "OBJECTID", range(1, len(gdf) + 1))
        
        gdf["source"] = "additional"
        return gdf
        
    except:
        return gpd.GeoDataFrame()

def load_all_data():
    """LOAD SEMUA DATA = Main + Additional"""
    gdf_main = load_main_data()
    gdf_additional = load_additional_data()
    
    if not gdf_main.empty and not gdf_additional.empty:
        gdf = gpd.GeoDataFrame(pd.concat([gdf_main, gdf_additional], ignore_index=True))
    elif not gdf_main.empty:
        gdf = gdf_main
    elif not gdf_additional.empty:
        gdf = gdf_additional
    else:
        gdf = gpd.GeoDataFrame()
    
    return gdf

def save_additional_data(gdf: gpd.GeoDataFrame):
    """Save data tambahan ke file"""
    try:
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        gdf.to_file(str(ADDITIONAL_DATA_FILE), driver="GeoJSON")
        st.success("✅ Data tambahan disimpan!")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def read_shp_from_zip(uploaded_file):
    """Support SHP, KML, KMZ, GDB"""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = os.path.join(tmpdir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(temp_path, "r") as z:
                z.extractall(tmpdir)
            
            shp_files = list(Path(tmpdir).rglob("*.shp"))
            if shp_files:
                gdf = gpd.read_file(str(shp_files[0]))
            else:
                gdb_files = list(Path(tmpdir).rglob("*.gdb"))
                if gdb_files:
                    gdf = gpd.read_file(str(gdb_files[0]))
                else:
                    raise ValueError("Tidak ada .shp atau .gdb di ZIP")
        
        elif uploaded_file.name.endswith('.kml'):
            gdf = gpd.read_file(temp_path, driver='KML')
        
        elif uploaded_file.name.endswith('.kmz'):
            with zipfile.ZipFile(temp_path, "r") as z:
                z.extractall(tmpdir)
            kml_files = list(Path(tmpdir).rglob("*.kml"))
            if kml_files:
                gdf = gpd.read_file(str(kml_files[0]), driver='KML')
            else:
                raise ValueError("Tidak ada .kml di KMZ")
        else:
            raise ValueError(f"Format {uploaded_file.name} tidak didukung")
        
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        if "OBJECTID" not in gdf.columns:
            gdf.insert(0, "OBJECTID", range(1, len(gdf) + 1))
        
        return gdf

def center_map(gdf):
    try:
        if gdf.empty:
            return [-6.99, 107.55], 13
        c = gdf.geometry.unary_union.centroid
        return [c.y, c.x], 13
    except:
        return [-6.99, 107.55], 13

def display_cols(df):
    return [c for c in df.columns if c != "geometry" and c != "source"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 LOAD DATA SAAT APP START
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

gdf = load_all_data()
gdf_kabupaten = load_boundary(KABUPATEN_FILE)
gdf_kecamatan = load_boundary(KECAMATAN_FILE)
gdf_rtrw = load_boundary(RTRW_FILE)

# ✅ DEBUG: Show what files were found
with st.sidebar:
    st.markdown("### 📁 File yang ter-detect:")
    st.write(f"📍 DATA UTAMA: {'✅' if DATA_FILE else '❌'} {DATA_FILE.name if DATA_FILE else 'Tidak ditemukan'}")
    st.write(f"📍 KABUPATEN: {'✅' if KABUPATEN_FILE else '❌'} {KABUPATEN_FILE.name if KABUPATEN_FILE else 'Tidak ditemukan'}")
    st.write(f"📍 KECAMATAN: {'✅' if KECAMATAN_FILE else '❌'} {KECAMATAN_FILE.name if KECAMATAN_FILE else 'Tidak ditemukan'}")
    st.write(f"📍 RTRW: {'✅' if RTRW_FILE else '❌'} {RTRW_FILE.name if RTRW_FILE else 'Tidak ditemukan'}")
    st.write(f"📊 Total data loaded: {len(gdf)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 HEADER & NAVIGATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

header_html = f"""
<div class="header-gold-bar">
    <div class="header-left">
        {"<img src=\"data:image/png;base64," + logo_base64 + "\" class=\"header-logo-img\" alt=\"Logo\">" if logo_exists and logo_base64 else "<div class=\"header-logo-placeholder\">🗺️</div>"}
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗺️ PETA", use_container_width=True, key="nav_peta"):
        st.session_state.current_page = "peta"
        st.rerun()
with col2:
    if st.button("📋 TENTANG", use_container_width=True, key="nav_about"):
        st.session_state.current_page = "beranda"
        st.rerun()
with col3:
    if st.button("🔐 ADMIN", use_container_width=True, key="nav_admin"):
        st.session_state.current_page = "admin"
        st.rerun()

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# 📍 PAGE: LANDING
# ════════════════════════════════════════════════════════════════════════════

if st.session_state.current_page == "landing":
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🗺️ WebGIS Pemanfaatan Ruang</h1>
        <p class="hero-subtitle">Platform Geospasial Terdepan untuk Manajemen Data</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Visualisasi Interaktif</div>
            <div class="feature-desc">Peta interaktif dengan multi-layer dan filter advanced</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📤</div>
            <div class="feature-title">Upload Data Tambahan</div>
            <div class="feature-desc">Tambahkan data baru via admin panel</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔐</div>
            <div class="feature-title">Admin Dashboard</div>
            <div class="feature-desc">Kelola data tambahan dengan aman</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Database Kami")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{len(gdf)}</div><div class="stat-label">📍 Total Data</div></div>', unsafe_allow_html=True)
    with col2:
        n = gdf["PEMANFAATAN RUANG"].nunique() if "PEMANFAATAN RUANG" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number">{n}</div><div class="stat-label">🏙️ Jenis</div></div>', unsafe_allow_html=True)
    with col3:
        n = gdf["PERATURAN ZONASI"].nunique() if "PERATURAN ZONASI" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number">{n}</div><div class="stat-label">📋 Zonasi</div></div>', unsafe_allow_html=True)
    with col4:
        n = gdf["TAHUN"].nunique() if "TAHUN" in gdf.columns else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number">{n}</div><div class="stat-label">📅 Tahun</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 📍 PAGE: PETA
# ════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "peta":
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Peta Publik Pemanfaatan Ruang</h1>
        <p class="hero-subtitle">Visualisasi & Filter Data Geospasial</p>
    </div>
    """, unsafe_allow_html=True)

    if gdf.empty:
        st.error("❌ TIDAK ADA DATA!")
        st.info(f"""
        ℹ️ Pastikan file sudah berada di folder `data/`
        
        File yang harus ada:
        - `data/DATA_PEMANFAATAN.geojson` (UTAMA)
        - `data/Batas_Kabupaten.geojson` (Optional)
        - `data/Batas_Kecamatan.geojson` (Optional)
        - `data/RTRW.geojson` (Optional)
        
        Struktur folder:
        ```
        project/
        ├── app.py
        └── data/
            ├── DATA_PEMANFAATAN.geojson
            ├── Batas_Kabupaten.geojson
            ├── Batas_Kecamatan.geojson
            └── RTRW.geojson
        ```
        
        Reload app setelah menambah file: `F5` atau `Ctrl+R`
        """)
    else:
        # PREPARE FILTER OPTIONS
        tahun_opts = ["Semua"] + sorted(gdf["TAHUN"].dropna().astype(str).unique().tolist()) if "TAHUN" in gdf.columns else ["Semua"]
        pmnft_opts = ["Semua"] + sorted(gdf["PEMANFAATAN RUANG"].dropna().astype(str).unique().tolist()) if "PEMANFAATAN RUANG" in gdf.columns else ["Semua"]
        zona_opts = ["Semua"] + sorted(gdf["PERATURAN ZONASI"].dropna().astype(str).unique().tolist()) if "PERATURAN ZONASI" in gdf.columns else ["Semua"]

        # RENDER FILTER
        st.markdown("**🔍 Filter Data:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write('<p class="filter-label">📅 TAHUN</p>', unsafe_allow_html=True)
            f_tahun = st.selectbox("Tahun", tahun_opts, label_visibility="collapsed", key="tahun_filter")
        
        with col2:
            st.write('<p class="filter-label">🏙️ PEMANFAATAN</p>', unsafe_allow_html=True)
            f_pmnft = st.selectbox("Pemanfaatan", pmnft_opts, label_visibility="collapsed", key="pmnft_filter")
        
        with col3:
            st.write('<p class="filter-label">📋 ZONASI</p>', unsafe_allow_html=True)
            f_zona = st.selectbox("Zonasi", zona_opts, label_visibility="collapsed", key="zona_filter")
        
        with col4:
            st.write('<p class="filter-label">🔍 CARI</p>', unsafe_allow_html=True)
            f_kw = st.text_input("Cari Keyword", label_visibility="collapsed", placeholder="Keyword...", key="search_filter")

        # APPLY FILTERS
        fgdf = gdf.copy()
        is_filtered = False
        
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

        st.markdown(f"**📊 Menampilkan {len(fgdf)} dari {len(gdf)} data**")
        
        if is_filtered:
            st.info("🔍 Filter aktif - Data hasil filter di-highlight")

        # RENDER MAP
        with st.spinner("⏳ Memuat peta…"):
            center, zoom = center_map(fgdf if not fgdf.empty else gdf)
            m = leafmap.Map(center=center, zoom=zoom, height=500)
            m.add_basemap("OpenStreetMap")
            
            if not gdf_kabupaten.empty:
                m.add_gdf(gdf_kabupaten, layer_name="📍 Batas Kabupaten",
                    style={"color":"#2d6a4f","fillColor":"#2d6a4f","fillOpacity":0.04,"weight":2.0},
                    info_mode="on_hover")
            
            if not gdf_kecamatan.empty:
                m.add_gdf(gdf_kecamatan, layer_name="📍 Batas Kecamatan",
                    style={"color":"#e07b39","fillColor":"#e07b39","fillOpacity":0.06,"weight":2.5},
                    info_mode="on_hover")
            
            if not is_filtered and not gdf_rtrw.empty:
                m.add_gdf(gdf_rtrw, layer_name="🏗️ RTRW",
                    style={"color":"#ff6b6b","fillColor":"#ff6b6b","fillOpacity":0.08,"weight":2.0},
                    info_mode="on_hover")
            
            if not fgdf.empty:
                if is_filtered:
                    m.add_gdf(fgdf, layer_name="✨ Hasil Filter",
                        style={"color":"#FFD700","fillColor":"#FFD700","fillOpacity":0.55,"weight":2.5},
                        info_mode="on_click")
                else:
                    m.add_gdf(fgdf, layer_name="📍 Pemanfaatan Ruang",
                        style={"color":"#1a3a52","fillColor":"#FFD700","fillOpacity":0.35,"weight":1.5},
                        info_mode="on_click")

            try:
                m.to_streamlit(height=500)
            except Exception as e:
                st.error(f"⚠️ Error render map: {str(e)}")

        # DATA TABLE
        if not fgdf.empty:
            st.subheader("📋 Data Detail")
            st.dataframe(fgdf[display_cols(fgdf)], use_container_width=True, height=300)

# ════════════════════════════════════════════════════════════════════════════
# 📍 PAGE: ADMIN
# ════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "admin":
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🔐 Admin Panel</h1>
        <p class="hero-subtitle">Kelola Data Tambahan</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        st.warning("🔒 Silakan login terlebih dahulu")
        with st.form("login_form"):
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🔓 Login", use_container_width=True):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Password salah!")
    else:
        st.success("✅ Login sebagai Admin")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

        tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Tambahan", "🗑️ Hapus Tambahan", "📥 Export", "ℹ️ Info"])
        
        with tab1:
            st.subheader("📤 Upload Data Tambahan")
            
            st.info("""
            ✅ **Data utama sudah ada** (dimuat otomatis dari file)
            
            Di sini Anda bisa upload data TAMBAHAN untuk menambah data yang sudah ada.
            """)
            
            uploaded_file = st.file_uploader("Upload File Geospasial", type=["zip", "kml", "kmz", "geojson"])
            
            if uploaded_file:
                try:
                    st.info(f"📁 File: {uploaded_file.name}")
                    shp = read_shp_from_zip(uploaded_file)
                    
                    st.success(f"✅ File valid! ({len(shp)} features)")
                    st.dataframe(shp[display_cols(shp)].head(3), use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Simpan Data Tambahan", use_container_width=True, type="primary"):
                            save_additional_data(shp)
                            st.rerun()
                    with col2:
                        if st.button("❌ Batal"):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with tab2:
            st.subheader("🗑️ Hapus Data Tambahan")
            
            gdf_additional = load_additional_data()
            
            if gdf_additional.empty:
                st.info("📭 Tidak ada data tambahan")
            else:
                st.warning(f"⚠️ Akan menghapus {len(gdf_additional)} data tambahan")
                
                if st.button("🗑️ HAPUS SEMUA DATA TAMBAHAN", use_container_width=True, type="secondary"):
                    if ADDITIONAL_DATA_FILE.exists():
                        ADDITIONAL_DATA_FILE.unlink()
                    st.success("✅ Data tambahan dihapus!")
                    st.rerun()
        
        with tab3:
            st.subheader("📥 Export Data")
            
            if not gdf.empty:
                st.download_button(
                    "📥 Download Semua Data",
                    gdf.drop(columns=["source"], errors="ignore").to_json(),
                    "data_all.geojson",
                    "application/geo+json",
                    use_container_width=True
                )
        
        with tab4:
            st.subheader("ℹ️ Informasi Data")
            
            gdf_main = load_main_data()
            gdf_additional = load_additional_data()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📍 Data Utama (Main Database)", len(gdf_main))
            with col2:
                st.metric("📤 Data Tambahan (User Upload)", len(gdf_additional))
            
            st.markdown("---")
            st.markdown(f"""
            **📁 Lokasi File:**
            - Main data: `{DATA_FILE}`
            - Additional data: `{ADDITIONAL_DATA_FILE}`
            """)

# ════════════════════════════════════════════════════════════════════════════
# 📍 PAGE: TENTANG
# ════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "beranda":
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Tentang Platform</h1>
        <p class="hero-subtitle">Solusi Geospasial untuk Pemanfaatan Ruang</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 📋 Tentang Platform
    
    WebGIS Pemanfaatan Ruang adalah sistem informasi geospasial yang dirancang untuk:
    
    - 🗺️ Visualisasi data pemanfaatan ruang
    - 📊 Analisis dan filter data
    - 📤 Upload data tambahan via admin
    - 🔐 Manajemen data terstruktur
    
    ### 🎯 Cara Kerja
    
    1. **Data Utama** → Otomatis dimuat dari folder `data/`
    2. **Data Tambahan** → Upload via admin panel
    3. **Peta Publik** → Semua orang bisa lihat tanpa login
    4. **Admin Panel** → Password-protected untuk upload data baru
    """)

# ════════════════════════════════════════════════════════════════════════════
# 🔚 FOOTER
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div class="footer">
    <p>© 2025 WebGIS Pemanfaatan Ruang — Platform Geospasial Terdepan</p>
    <p style="font-size: 0.8rem;">Dikembangkan untuk manajemen data yang lebih baik</p>
</div>
""", unsafe_allow_html=True)
