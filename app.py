import streamlit as st
import random
import pandas as pd
import time
import io
import base64
from pathlib import Path
import streamlit.components.v1 as components

# Fungsi untuk memutar suara berbasis base64 (agar autoplay stabil)
def play_audio_base64(file_path):
    path = Path(file_path)
    if path.exists():
        b64 = base64.b64encode(path.read_bytes()).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        components.html(audio_html, height=0)

# Konfigurasi halaman
st.set_page_config(page_title="Undian Hadiah", layout="centered")

# Inisialisasi session state
if 'peserta' not in st.session_state:
    st.session_state.peserta = []
if 'hadiah' not in st.session_state:
    st.session_state.hadiah = []
if 'hasil' not in st.session_state:
    st.session_state.hasil = []
if 'terundi' not in st.session_state:
    st.session_state.terundi = 0
if 'undian_dimulai' not in st.session_state:
    st.session_state.undian_dimulai = False
if 'show_overlay' not in st.session_state:
    st.session_state.show_overlay = False
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'terpilih' not in st.session_state:
    st.session_state.terpilih = ("", "")
if 'suara' not in st.session_state:
    st.session_state.suara = "assets/sound.mp3"

# Judul
st.title("🎁 Undian Hadiah Peserta")

# Tombol reset
if st.button("🔄 Reset Semua"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Input peserta
st.subheader("👥 Tambah Peserta")
with st.form("form_peserta"):
    nama = st.text_input("Nama Peserta")
    simpan = st.form_submit_button("➕ Tambahkan")
    if simpan and nama.strip():
        st.session_state.peserta.append(nama.strip())
        st.success(f"Peserta ditambahkan: {nama.strip()}")
        st.rerun()

if st.session_state.peserta:
    st.markdown("### Daftar Peserta")
    for i, p in enumerate(st.session_state.peserta):
        col1, col2 = st.columns([7, 1])
        with col1:
            st.text_input(f"Peserta {i+1}", value=p, key=f"peserta_{i}", disabled=True)
        with col2:
            if st.button("🗑️", key=f"hapus_peserta_{i}"):
                st.session_state.peserta.pop(i)
                st.rerun()

# Input hadiah
st.subheader("🎁 Tambah Hadiah (termasuk ZONK)")
with st.form("form_hadiah"):
    hadiah = st.text_input("Nama Hadiah")
    simpan_hadiah = st.form_submit_button("➕ Tambahkan Hadiah")
    if simpan_hadiah and hadiah.strip():
        st.session_state.hadiah.append(hadiah.strip())
        st.success(f"Hadiah ditambahkan: {hadiah.strip()}")
        st.rerun()

if st.session_state.hadiah:
    st.markdown("### Daftar Hadiah")
    for i, h in enumerate(st.session_state.hadiah):
        col1, col2 = st.columns([7, 1])
        with col1:
            st.text_input(f"Hadiah {i+1}", value=h, key=f"hadiah_{i}", disabled=True)
        with col2:
            if st.button("🗑️", key=f"hapus_hadiah_{i}"):
                st.session_state.hadiah.pop(i)
                st.rerun()

# Proses undian
if st.session_state.peserta and st.session_state.hadiah:
    if len(st.session_state.peserta) != len(st.session_state.hadiah):
        st.warning("⚠️ Jumlah peserta dan hadiah harus sama.")
    elif not st.session_state.undian_dimulai:
        if st.button("🎲 MULAI UNDIAN"):
            random.shuffle(st.session_state.peserta)
            random.shuffle(st.session_state.hadiah)
            st.session_state.undian_dimulai = True
            st.rerun()
    elif st.session_state.terundi < len(st.session_state.peserta):
        if st.button("➡️ Undi Berikutnya"):
            i = st.session_state.terundi
            peserta = st.session_state.peserta[i]
            hadiah = st.session_state.hadiah[i]
            st.session_state.hasil.append((peserta, hadiah))
            st.session_state.terundi += 1
            st.session_state.terpilih = (peserta, hadiah)
            st.session_state.suara = "assets/zonk.mp3" if "zonk" in hadiah.lower() else "assets/sound.mp3"
            st.session_state.show_overlay = True
            st.rerun()

# Tampilkan overlay + SUARA saat loading
if st.session_state.show_overlay:
    overlay = st.empty()

    # ✅ Putar suara saat countdown dimulai
    play_audio_base64(st.session_state.suara)

    for i in range(5, 0, -1):
        overlay.markdown(f"""
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                         background-color: rgba(0,0,0,0.85); color: white; display: flex;
                         justify-content: center; align-items: center; font-size: 60px;
                         z-index: 9999; text-shadow: 2px 2px 5px black;">
                ⏳ Mengundi... {i}
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)

    overlay.empty()
    st.session_state.show_overlay = False
    st.session_state.show_result = True
    st.rerun()

# Tampilkan hasil undian
if st.session_state.show_result:
    peserta, hadiah = st.session_state.terpilih
    result_popup = st.empty()

    try:
        bg_path = "assets/zonk.png" if "zonk" in hadiah.lower() else "assets/celebration.png"
        with open(bg_path, "rb") as image_file:
            encoded_bg = base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        encoded_bg = ""

    warna_teks = "#ff0000" if "zonk" in hadiah.lower() else "#00ffcc"
    teks = f"😢 {peserta} kena ZONK!" if "zonk" in hadiah.lower() else f"🎉 {peserta} mendapatkan: {hadiah}"

    result_popup.markdown(f"""
        <style>
        @keyframes zoomIn {{
            0% {{ opacity: 0; transform: scale(0.5); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}
        .popup {{
            animation: zoomIn 0.6s ease-out;
            background: url("data:image/png;base64,{encoded_bg}");
            background-size: cover;
            background-position: center;
            width: 100%;
            height: 100%;
            position: fixed;
            top: 0; left: 0;
            z-index: 9999;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            text-shadow: 2px 2px 5px #000;
        }}
        </style>
        <div class="popup">
            <div style='font-size: 48px;'>🎁 Hasil Undian:</div>
            <div style='font-size: 64px; font-weight: bold; margin-top: 10px; color: {warna_teks};'>
                {teks}
            </div>
        </div>
    """, unsafe_allow_html=True)

    time.sleep(7)
    result_popup.empty()
    st.session_state.show_result = False

# Tabel hasil dan download
if st.session_state.hasil:
    st.subheader("📜 Hasil Undian")
    df = pd.DataFrame(st.session_state.hasil, columns=["Peserta", "Hadiah"])
    st.dataframe(df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil')
    st.download_button(
        label="📥 Download Excel",
        data=output.getvalue(),
        file_name="hasil_undian.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
