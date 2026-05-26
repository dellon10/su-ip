import streamlit as st
import pandas as pd
# import plotly.express as px # Jika ingin menggunakan grafik plotly
# from wordcloud import WordCloud # Jika ingin menggunakan wordcloud

st.set_page_config(page_title="Dashboard Kelud", layout="wide")
st.title("🌋 Dashboard Analisis Sentimen Wisata")

# --- 1. MEMBACA DATA ---
df = pd.read_csv("dataset_kelud_mei.csv")
# (Asumsi Anda sudah menjalankan model/proses untuk menambahkan kolom 'sentimen')

# --- 2. SIDEBAR FILTER ---
bulan = st.sidebar.selectbox("Pilih Bulan", ["Mei", "Juni"])
# filter_sentimen = st.sidebar.multiselect("Pilih Sentimen", ["Positif", "Netral", "Negatif"])

# --- 3. METRIKS UTAMA ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Ulasan", value=len(df))
with col2:
    st.metric(label="Sentimen Positif", value="75%", delta="Bagus")
with col3:
    st.metric(label="Sentimen Negatif", value="25%", delta="-5%", delta_color="inverse")

st.markdown("---")

# --- 4. GRAFIK & VISUALISASI ---
col_grafik1, col_grafik2 = st.columns(2)
with col_grafik1:
    st.subheader("Persentase Sentimen")
    # Tampilkan Pie Chart atau Bar Chart di sini
    
with col_grafik2:
    st.subheader("Kata yang Sering Muncul (Word Cloud)")
    # Tampilkan gambar Word Cloud di sini

st.markdown("---")

# --- 5. TABEL DATA MENTAH ---
st.subheader("Data Ulasan Pengunjung")
st.dataframe(df)