import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from io import BytesIO

# ── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Sentimen Kelud",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #f8f7f4;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border: 0.5px solid #e0ddd6;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f1efe8 !important;
    border-right: 0.5px solid #d3d1c7;
}
[data-testid="stSidebar"] h2 {
    font-size: 16px !important;
}

/* Divider */
hr { border: none; border-top: 0.5px solid #d3d1c7; margin: 1.5rem 0; }

/* Badge / pill */
.pill-positif  { background:#e1f5ee; color:#085041; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:500; }
.pill-negatif  { background:#faece7; color:#993c1d; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:500; }
.pill-netral   { background:#faeeda; color:#633806; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:500; }

/* Scrollable table area */
.scrollable { max-height: 340px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

# ── WARNA TEMA ───────────────────────────────────────────────────────────────
C_POS    = "#1D9E75"   # hijau
C_NEG    = "#C0392B"   # merah
C_NEU    = "#EF9F27"   # amber
C_SKY    = "#185FA5"   # biru
C_BG     = "#f8f7f4"

# ── DATA (ganti dengan CSV asli) ──────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dataset_kelud_mei.csv")
    except FileNotFoundError:
        # Data demo jika CSV belum ada
        np.random.seed(42)
        n = 248
        ulasan_list = [
            "Pemandangan luar biasa, danau kawah sangat memukau!",
            "Jalanan menuju lokasi sangat rusak dan berlubang.",
            "Tempat wisata yang bersih dan terawat dengan baik.",
            "Harga tiket masuk cukup terjangkau untuk keluarga.",
            "Parkir sangat sempit dan jauh dari lokasi utama.",
            "Udara sejuk dan segar, cocok untuk piknik akhir pekan.",
            "Warung makan pilihan menunya sangat terbatas.",
            "Spot foto keren banget, banyak sudut Instagramable!",
            "Petugas ramah dan membantu pengunjung dengan baik.",
            "Toalet umum kurang bersih dan tidak terawat.",
        ]
        sentimen_opts = ["Positif", "Positif", "Positif", "Netral", "Negatif", "Positif", "Netral", "Positif", "Positif", "Negatif"]
        aspek_opts = ["Pemandangan","Akses Jalan","Kebersihan","Fasilitas","Parkir","Pemandangan","Fasilitas","Pemandangan","Fasilitas","Kebersihan"]
        idx = np.random.randint(0, len(ulasan_list), n)
        df = pd.DataFrame({
            "ulasan":   [ulasan_list[i] for i in idx],
            "sentimen": [sentimen_opts[i] for i in idx],
            "aspek":    [aspek_opts[i] for i in idx],
            "skor":     np.clip(np.random.normal(0.65, 0.25, n), 0.05, 0.99).round(2),
            "bulan":    np.random.choice(["Mei", "Juni"], n, p=[0.6, 0.4]),
        })
    # Pastikan kolom sentimen ada
    if "sentimen" not in df.columns:
        df["sentimen"] = "Netral"
    return df

df_all = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌋 Filter Data")
    st.markdown("---")

    bulan_opts = ["Semua"] + sorted(df_all["bulan"].unique().tolist()) if "bulan" in df_all.columns else ["Semua"]
    bulan_sel  = st.selectbox("📅 Pilih Bulan", bulan_opts)

    sentimen_opts_filter = ["Semua", "Positif", "Netral", "Negatif"]
    sentimen_sel = st.multiselect("💬 Pilih Sentimen", ["Positif", "Netral", "Negatif"], default=["Positif","Netral","Negatif"])

    aspek_list = sorted(df_all["aspek"].unique().tolist()) if "aspek" in df_all.columns else []
    if aspek_list:
        aspek_sel = st.multiselect("🏷️ Pilih Aspek", aspek_list, default=aspek_list)
    else:
        aspek_sel = []

    st.markdown("---")
    st.caption("Dashboard Analisis Sentimen\nGunung Kelud © 2025")

# ── FILTER ───────────────────────────────────────────────────────────────────
df = df_all.copy()
if bulan_sel != "Semua" and "bulan" in df.columns:
    df = df[df["bulan"] == bulan_sel]
if sentimen_sel:
    df = df[df["sentimen"].isin(sentimen_sel)]
if aspek_sel and "aspek" in df.columns:
    df = df[df["aspek"].isin(aspek_sel)]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:0.5rem;">
  <div>
    <h1 style="margin:0;font-size:28px;">🌋 Dashboard Sentimen Wisata Kelud</h1>
    <p style="color:#888780;margin-top:4px;font-size:14px;">Analisis ulasan pengunjung berbasis NLP</p>
  </div>
  <span style="background:#faece7;color:#993c1d;border-radius:20px;padding:5px 16px;font-size:13px;font-weight:500;border:0.5px solid #f0997b;">
    🔥 {bulan} 2025
  </span>
</div>
""".format(bulan=bulan_sel if bulan_sel != "Semua" else "Semua Bulan"), unsafe_allow_html=True)
st.markdown("---")

# ── METRIK ───────────────────────────────────────────────────────────────────
total   = len(df)
n_pos   = (df["sentimen"] == "Positif").sum()
n_neg   = (df["sentimen"] == "Negatif").sum()
n_neu   = (df["sentimen"] == "Netral").sum()
pct_pos = round(n_pos / total * 100) if total else 0
pct_neg = round(n_neg / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 Total Ulasan",      total,            f"+{total} ulasan")
col2.metric("✅ Sentimen Positif",  f"{pct_pos}%",    "Sangat baik" if pct_pos >= 70 else "Cukup baik")
col3.metric("❌ Sentimen Negatif",  f"{pct_neg}%",    f"{pct_neg - 25:+d}% vs rata-rata", delta_color="inverse")
col4.metric("➖ Sentimen Netral",   f"{round(n_neu/total*100) if total else 0}%", f"{n_neu} ulasan")

st.markdown("---")

# ── GRAFIK BARIS 1 ────────────────────────────────────────────────────────────
col_g1, col_g2 = st.columns([1, 1.4])

with col_g1:
    st.subheader("Distribusi Sentimen")
    pie_data = df["sentimen"].value_counts().reset_index()
    pie_data.columns = ["Sentimen", "Jumlah"]
    color_map = {"Positif": C_POS, "Negatif": C_NEG, "Netral": C_NEU}
    fig_pie = px.pie(
        pie_data, names="Sentimen", values="Jumlah",
        color="Sentimen", color_discrete_map=color_map,
        hole=0.55,
    )
    fig_pie.update_traces(textinfo="percent+label", textfont_size=13,
                          marker=dict(line=dict(color="#ffffff", width=3)))
    fig_pie.update_layout(
        showlegend=True, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=280,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_g2:
    st.subheader("Aspek Ulasan Terpopuler")
    if "aspek" in df.columns:
        aspek_counts = df.groupby(["aspek","sentimen"]).size().reset_index(name="n")
        fig_bar = px.bar(
            aspek_counts, x="n", y="aspek", color="sentimen",
            color_discrete_map=color_map, orientation="h",
            barmode="stack",
        )
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=0, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Jumlah Ulasan", yaxis_title="",
            legend_title="Sentimen",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            height=280,
            yaxis=dict(categoryorder="total ascending"),
        )
        fig_bar.update_xaxes(showgrid=True, gridcolor="#e0ddd6")
        fig_bar.update_yaxes(showgrid=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Kolom 'aspek' tidak ditemukan di dataset.")

st.markdown("---")

# ── WORD CLOUD ────────────────────────────────────────────────────────────────
col_wc1, col_wc2 = st.columns(2)

def buat_wordcloud(teks_series, colormap, judul):
    teks_gabung = " ".join(teks_series.dropna().tolist())
    if not teks_gabung.strip():
        st.info(f"Tidak ada data untuk {judul}.")
        return
    wc = WordCloud(
        width=700, height=350,
        background_color=None, mode="RGBA",
        colormap=colormap,
        max_words=60,
        prefer_horizontal=0.85,
        font_path=None,
        collocations=False,
        min_font_size=11,
    ).generate(teks_gabung)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0)
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

with col_wc1:
    st.subheader("☁️ Kata — Ulasan Positif")
    buat_wordcloud(df[df["sentimen"] == "Positif"]["ulasan"], "Greens", "Positif")

with col_wc2:
    st.subheader("☁️ Kata — Ulasan Negatif")
    buat_wordcloud(df[df["sentimen"] == "Negatif"]["ulasan"], "Reds", "Negatif")

st.markdown("---")

# ── TREN WAKTU (jika ada kolom tanggal) ──────────────────────────────────────
if "tanggal" in df.columns:
    st.subheader("📈 Tren Sentimen per Waktu")
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    tren = df.groupby([df["tanggal"].dt.to_period("W").astype(str), "sentimen"]).size().reset_index(name="n")
    fig_tren = px.line(
        tren, x="tanggal", y="n", color="sentimen",
        color_discrete_map=color_map, markers=True,
    )
    fig_tren.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Minggu", yaxis_title="Jumlah Ulasan",
        legend_title="Sentimen", height=300,
        margin=dict(t=10, b=10),
    )
    fig_tren.update_xaxes(showgrid=True, gridcolor="#e0ddd6")
    fig_tren.update_yaxes(showgrid=True, gridcolor="#e0ddd6")
    st.plotly_chart(fig_tren, use_container_width=True)
    st.markdown("---")

# ── TABEL DATA MENTAH ─────────────────────────────────────────────────────────
st.subheader("📄 Data Ulasan Pengunjung")

search_q = st.text_input("🔍 Cari ulasan...", placeholder="ketik kata kunci...")
df_view = df.copy()
if search_q:
    df_view = df_view[df_view["ulasan"].str.contains(search_q, case=False, na=False)]

def warnai_sentimen(val):
    warna = {"Positif": "#e1f5ee", "Negatif": "#faece7", "Netral": "#faeeda"}
    teks  = {"Positif": "#085041", "Negatif": "#993c1d", "Netral": "#633806"}
    bg = warna.get(val, "#f8f7f4")
    fg = teks.get(val, "#2c2c2a")
    return f"background-color:{bg};color:{fg};border-radius:20px;padding:2px 10px;font-weight:500;"

styled = df_view.style.applymap(warnai_sentimen, subset=["sentimen"])
if "skor" in df_view.columns:
    styled = styled.background_gradient(subset=["skor"], cmap="RdYlGn", vmin=0, vmax=1)

st.dataframe(styled, use_container_width=True, height=360)
st.caption(f"Menampilkan {len(df_view):,} dari {len(df):,} ulasan")

# ── DOWNLOAD ─────────────────────────────────────────────────────────────────
csv_bytes = df_view.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Unduh Data yang Ditampilkan (CSV)",
    data=csv_bytes,
    file_name="ulasan_kelud_filtered.csv",
    mime="text/csv",
)