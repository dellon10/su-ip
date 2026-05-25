import streamlit as st
import pandas as pd

st.title("Analisis Sentimen")

df = pd.read_csv("dataset_kelud_mei.csv")

df['tanggal'] = pd.to_datetime(df['tanggal'])

bulan = st.selectbox(
    "Pilih Bulan",
    ["Mei", "Juni"]
)

if bulan == "Mei":
    filtered = df[df['tanggal'].dt.month == 5]
else:
    filtered = df[df['tanggal'].dt.month == 6]

st.dataframe(filtered)

st.bar_chart(filtered['sentimen'].value_counts())