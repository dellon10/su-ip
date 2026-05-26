import streamlit as st
import pandas as pd

st.title("Analisis Sentimen")

# 1. Membaca dataset asli
df = pd.read_csv("dataset_kelud_mei.csv")

# 2. Fungsi kustom untuk mengubah teks relatif menjadi angka bulan
def konversi_ke_bulan(teks_waktu):
    if pd.isna(teks_waktu):
        return None
    
    teks = str(teks_waktu).lower()
    
    # Pemetaan teks ke bulan (Asumsi saat ini adalah akhir Mei/Juni)
    if "4 minggu" in teks or "sebulan" in teks:
        return 5  # Bulan Mei
    elif "2 bulan" in teks:
        return 4  # Bulan April (bisa disesuaikan jika ini maksudnya Juni)
    # Anda bisa menambah kondisi elif lain di sini jika ada format teks baru
    
    return None

# 3. Buat kolom baru 'bulan_angka' berdasarkan fungsi di atas
df['bulan_angka'] = df['waktu'].apply(konversi_ke_bulan)

# 4. Input pilihan dari user
bulan = st.selectbox(
    "Pilih Bulan",
    ["Mei", "Juni"]
)

# 5. Filter data berdasarkan pilihan
if bulan == "Mei":
    filtered = df[df['bulan_angka'] == 5]
else:
    filtered = df[df['bulan_angka'] == 6]

# 6. Hapus kolom pembantu 'bulan_angka' sebelum ditampilkan agar tabel rapi
tampilan_df = filtered.drop(columns=['bulan_angka'], errors='ignore')

# 7. Tampilkan hasil ke Streamlit
st.dataframe(tampilan_df)