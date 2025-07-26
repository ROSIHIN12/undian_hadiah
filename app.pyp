import streamlit as st
import random
import pandas as pd
import time
import io
import base64

st.set_page_config(page_title="Undian Hadiah untuk Peserta", layout="centered")

# Inisialisasi state
if 'hadiah' not in st.session_state:
    st.session_state.hadiah = []
if 'hasil' not in st.session_state:
    st.session_state.hasil = []  # list of tuple: (peserta, hadiah)
if 'show_overlay' not in st.session_state:
    st.session_state.show_overlay = False
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'terpilih' not in st.session_state:
    st.session_state.terpilih = None
if 'peserta_sekarang' not in st.session_state:
    st.session_state.peserta_sekarang = ""
if 'zonk_ditambahkan' not in st.session_state:
    st.session_state.zonk_ditambahkan = False

# Judul Aplikasi
st.title("🎁 Undian Hadiah Peserta")
st.markdown("Masukkan daftar hadiah terlebih dahulu. Saat memutar undian, masukkan nama peserta yang akan diundi. Akan ada 1 hadiah ZONK 🎲.")

# Tombol reset
if st.button("🔄 Reset"):
    st.session_state.hadiah = []
    st.session_state.hasil = []
    st.session_state.terpilih = None
    st.session_state.show_overlay = False
    st.session_state.show_result = False
    st.session_state.zonk_ditambahkan = False
    st.session_state.peserta_sekarang = ""
    st.rerun()

# Input hadiah
with st.form("form_hadiah"):
    hadiah = st.text_input("Nama Hadiah")
    simpan = st.form_submit_button("➕ Tambahkan Hadiah")
    if simpan and hadiah.strip():
        st.session_state.hadiah.append(hadiah.strip())
        st.success(f"Ditambahkan: {hadiah.strip()}")
        st.rerun()

# Tambahkan ZONK hanya satu kali
if st.session_state.hadiah and not st.session_state.zonk_ditambahkan:
    st.session_state.hadiah.append("🎲 ZONK")
    st.session_state.zonk_ditambahkan = True

# Tampilkan daftar hadiah
if st.session_state.hadiah:
    st.markdown("### 🎁 Daftar Hadiah Tersisa")
    for i, item in enumerate(st.session_state.hadiah):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.text_input(f"Hadiah {i+1}", value=item, key=f"hadiah_{i}", disabled=True)
        with col2:
            if st.button("🗑️", key=f"hapus_{i}"):
                st.session_state.hadiah.pop(i)
                st.warning(f"Hadiah ke-{i+1} dihapus.")
                st.rerun()

# Form input peserta saat akan memutar undian
if st.session_state.hadiah:
    with st.form("form_peserta"):
        st.session_state.peserta_sekarang = st.text_input("Nama Peserta yang Akan Diundi", value=st.session_state.peserta_sekarang)
        undi = st.form_submit_button("🎲 Putar Undian")
        if undi and st.session_state.peserta_sekarang.strip():
            st.session_state.show_overlay = True
            st.rerun()

# Pop-up Loading
if st.session_state.show_overlay:
    st.audio("assets/sound.mp3", autoplay=True)
    overlay = st.empty()
    for i in range(5, 0, -1):
        overlay.markdown(f"""
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                         background-color: rgba(0,0,0,0.85); color: white; display: flex;
                         justify-content: center; align-items: center; font-size: 40px; z-index: 9999;">
                🎡 Mengundi untuk {st.session_state.peserta_sekarang}... {i}
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)

    hadiah_terpilih = random.choice(st.session_state.hadiah)
    st.session_state.terpilih = (st.session_state.peserta_sekarang, hadiah_terpilih)
    st.session_state.hasil.append(st.session_state.terpilih)
    st.session_state.hadiah.remove(hadiah_terpilih)
    st.session_state.show_overlay = False
    st.session_state.show_result = True
    overlay.empty()
    st.rerun()

# Pop-up Hasil
if st.session_state.show_result:
    result_popup = st.empty()
    nama, hadiah = st.session_state.terpilih

    if "ZONK" in hadiah:
        # Jika hadiah adalah ZONK
        try:
            with open("assets/zonk.png", "rb") as image_file:
                encoded_bg = base64.b64encode(image_file.read()).decode()
        except FileNotFoundError:
            encoded_bg = ""

        st.audio("assets/zonk.mp3", autoplay=True)

        result_popup.markdown(f"""
            <style>
            @keyframes shake {{
                0% {{ transform: translateX(0); }}
                25% {{ transform: translateX(-10px); }}
                50% {{ transform: translateX(10px); }}
                75% {{ transform: translateX(-10px); }}
                100% {{ transform: translateX(0); }}
            }}
            .popup {{
                animation: shake 1s ease-in-out;
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
                <div style='font-size: 48px;'>😢 {nama} kena:</div>
                <div style='font-size: 64px; font-weight: bold; margin-top: 10px; color: #ff0000;'>
                    🎲 ZONK!
                </div>
            </div>
        """, unsafe_allow_html=True)

    else:
        # Hadiah normal
        try:
            with open("assets/celebration.png", "rb") as image_file:
                encoded_bg = base64.b64encode(image_file.read()).decode()
        except FileNotFoundError:
            encoded_bg = ""

        st.audio("assets/sound.mp3", autoplay=True)

        result_popup.markdown(f"""
            <style>
            @keyframes zoomIn {{
                0% {{ transform: scale(0.5); opacity: 0; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
            .popup {{
                animation: zoomIn 1s ease-out;
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
                <div style='font-size: 48px;'>🎉 {nama} mendapatkan:</div>
                <div style='font-size: 64px; font-weight: bold; margin-top: 10px; color: #00ffcc;'>
                    {hadiah}
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(8)
    result_popup.empty()
    st.session_state.show_result = False
    st.session_state.peserta_sekarang = ""


# Tabel hasil undian
if st.session_state.hasil:
    st.markdown("### 📋 Riwayat Undian")
    df = pd.DataFrame(st.session_state.hasil, columns=["Nama Peserta", "Hadiah"])
    st.dataframe(df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil Undian')
    st.download_button(
        label="📥 Download Hasil ke Excel",
        data=output.getvalue(),
        file_name="hasil_undian_peserta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
