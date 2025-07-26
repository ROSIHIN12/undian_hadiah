import streamlit as st
import random
import pandas as pd
import io
import time
import base64

st.set_page_config(page_title="Undian Hadiah Peserta", layout="centered")

# Fungsi putar suara HTML autoplay
def putar_suara(nama_file):
    st.markdown(f"""
        <audio autoplay>
            <source src="assets/{nama_file}" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)

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
if 'zonk_ditambahkan' not in st.session_state:
    st.session_state.zonk_ditambahkan = False
if 'sudah_diundi' not in st.session_state:
    st.session_state.sudah_diundi = set()

st.title("🎁 Undian Hadiah untuk Peserta")

# Tombol Reset
if st.button("🔄 Reset Semua"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Input Peserta
st.subheader("👥 Daftar Peserta")
input_peserta = st.text_area("Masukkan daftar peserta (satu nama per baris)", height=150)
if st.button("✅ Simpan Peserta"):
    st.session_state.peserta = [p.strip() for p in input_peserta.split('\n') if p.strip()]
    st.success("Daftar peserta disimpan.")

# Input Hadiah
st.subheader("🎁 Daftar Hadiah")
input_hadiah = st.text_area("Masukkan daftar hadiah (satu hadiah per baris)", height=150)
if st.button("✅ Simpan Hadiah"):
    hadiah_list = [h.strip() for h in input_hadiah.split('\n') if h.strip()]
    if "🎲 ZONK" not in hadiah_list:
        hadiah_list.append("🎲 ZONK")
    st.session_state.hadiah = hadiah_list
    st.success("Daftar hadiah disimpan (otomatis ditambahkan ZONK satu).")

# Validasi dan mulai undian
if st.session_state.peserta and st.session_state.hadiah:
    if len(st.session_state.peserta) != len(st.session_state.hadiah):
        st.warning(f"Jumlah peserta ({len(st.session_state.peserta)}) dan hadiah ({len(st.session_state.hadiah)}) harus sama.")
    else:
        if not st.session_state.undian_dimulai:
            if st.button("🎲 MULAI UNDIAN"):
                random.shuffle(st.session_state.peserta)
                random.shuffle(st.session_state.hadiah)
                st.session_state.undian_dimulai = True
                st.session_state.terundi = 0
                st.rerun()
        else:
            if st.session_state.terundi < len(st.session_state.peserta):
                if st.button("➡️ Undi Berikutnya"):
                    st.session_state.terundi += 1
                    st.rerun()

# Menampilkan hasil undian satu per satu
if st.session_state.undian_dimulai and st.session_state.terundi > 0:
    index = st.session_state.terundi - 1
    nama = st.session_state.peserta[index]
    hadiah = st.session_state.hadiah[index]

    if (nama, hadiah) not in st.session_state.sudah_diundi:
        st.session_state.hasil.append((nama, hadiah))
        st.session_state.sudah_diundi.add((nama, hadiah))

        result_popup = st.empty()

        if "ZONK" in hadiah.upper():
            putar_suara("zonk.mp3")
            try:
                with open("assets/zonk.png", "rb") as image_file:
                    encoded_bg = base64.b64encode(image_file.read()).decode()
            except:
                encoded_bg = ""

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
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                color: white;
                text-shadow: 2px 2px 5px black;
            }}
            </style>
            <div class="popup">
                <div style="font-size: 50px;">😢 {nama} kena:</div>
                <div style="font-size: 70px; font-weight: bold; color: red;">🎲 ZONK!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            putar_suara("sound.mp3")
            try:
                with open("assets/celebration.png", "rb") as image_file:
                    encoded_bg = base64.b64encode(image_file.read()).decode()
            except:
                encoded_bg = ""

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
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                color: white;
                text-shadow: 2px 2px 5px black;
            }}
            </style>
            <div class="popup">
                <div style="font-size: 50px;">🎉 {nama} mendapatkan:</div>
                <div style="font-size: 70px; font-weight: bold; color: #00ffcc;">{hadiah}</div>
            </div>
            """, unsafe_allow_html=True)

        time.sleep(6)
        result_popup.empty()

# Tampilkan hasil akhir
if st.session_state.hasil:
    st.subheader("📋 Riwayat Undian")
    df = pd.DataFrame(st.session_state.hasil, columns=["Peserta", "Hadiah"])
    st.dataframe(df, use_container_width=True)

    # Download Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil')
    st.download_button(
        label="📥 Download Hasil ke Excel",
        data=output.getvalue(),
        file_name="hasil_undian_peserta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
