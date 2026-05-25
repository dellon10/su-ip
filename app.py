import streamlit as st
import pandas as pd

st.title("Analisis Sentimen")

df = pd.read_csv("dataset.csv")

df['waktu'] = pd.to_datetime(df['waktu'])

bulan = st.selectbox(
    "Pilih Bulan",
    ["Mei", "Juni"]
)

if bulan == "Mei":
    filtered = df[df['waktu'].dt.month == 5]
else:
    filtered = df[df['waktu'].dt.month == 6]

st.dataframe(filtered)