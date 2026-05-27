import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Sentimen Kelud",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; font-weight: 700 !important; }

[data-testid="metric-container"] {
    background: #f8f7f4;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    border: 0.5px solid #e0ddd6;
}
[data-testid="stSidebar"] { background: #f1efe8 !important; border-right: 0.5px solid #d3d1c7; }
.stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

C_POS = "#1D9E75"
C_NEG = "#C0392B"

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("dataset_kelud_final_prediction.csv")
    df.columns = df.columns.str.strip().str.lower()

    # Normalise waktu → urutan kasar untuk sorting
    urutan = {
        "hari ini": 0, "kemarin": 1,
        "minggu lalu": 2, "2 minggu lalu": 3, "3 minggu lalu": 4, "4 minggu lalu": 5,
        "sebulan lalu": 6, "2 bulan lalu": 7, "3 bulan lalu": 8,
        "4 bulan lalu": 9, "5 bulan lalu": 10, "6 bulan lalu": 11,
        "setahun lalu": 12, "2 tahun lalu": 13, "3 tahun lalu": 14,
        "4 tahun lalu": 15, "5 tahun lalu": 16, "6 tahun lalu": 17,
        "7 tahun lalu": 18, "8 tahun lalu": 19, "9 tahun lalu": 20,
        "10 tahun lalu": 21,
    }
    df["waktu_urut"] = df["waktu"].str.strip().str.lower().map(urutan).fillna(99).astype(int)

    # Kelompok waktu untuk filter
    def grup_waktu(w):
        w = str(w).lower()
        if any(x in w for x in ["hari", "kemarin", "minggu"]):
            return "Minggu ini / bulan ini"
        if "bulan" in w:
            return "Beberapa bulan lalu"
        if w in ["setahun lalu", "2 tahun lalu", "3 tahun lalu"]:
            return "1–3 tahun lalu"
        return "4+ tahun lalu"

    df["grup_waktu"] = df["waktu"].apply(grup_waktu)
    return df

df_all = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌋 Filter")
    st.markdown("---")

    grup_opts = ["Semua"] + sorted(df_all["grup_waktu"].unique())
    grup_sel = st.selectbox("🕒 Periode Waktu", grup_opts)

    sentimen_sel = st.multiselect(
        "💬 Sentimen (Label Asli)",
        ["positif", "negatif"],
        default=["positif", "negatif"],
    )

    show_pred = st.toggle("Tampilkan kolom Prediksi Model", value=True)

    st.markdown("---")
    st.caption("Dashboard Sentimen Wisata\nGunung Kelud © 2025")

# ── FILTER ────────────────────────────────────────────────────────────────────
df = df_all.copy()
if grup_sel != "Semua":
    df = df[df["grup_waktu"] == grup_sel]
if sentimen_sel:
    df = df[df["label"].isin(sentimen_sel)]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:.25rem;">
  <div>
    <h1 style="margin:0;font-size:26px;color:#1a1a1a;">🌋 Dashboard Sentimen Wisata Kelud</h1>
    <p style="color:#888780;font-size:14px;margin-top:4px;">Analisis ulasan pengunjung · {} data</p>
  </div>
  <span style="background:#faece7;color:#993c1d;border-radius:20px;padding:5px 16px;font-size:12px;font-weight:500;border:0.5px solid #f0997b;">
    🔥 {} ulasan ditampilkan
  </span>
</div>
""".format(len(df_all), len(df)), unsafe_allow_html=True)
st.markdown("---")

# ── METRIK ────────────────────────────────────────────────────────────────────
total  = len(df)
n_pos  = (df["label"] == "positif").sum()
n_neg  = (df["label"] == "negatif").sum()
pct_pos = round(n_pos / total * 100) if total else 0
pct_neg = round(n_neg / total * 100) if total else 0

# Akurasi model
if "prediksi_model" in df.columns and total:
    benar = (df["label"] == df["prediksi_model"]).sum()
    akurasi = round(benar / total * 100, 1)
else:
    akurasi = None

c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 Total Ulasan",       total)
c2.metric("✅ Label Positif",      f"{pct_pos}%",  f"{n_pos} ulasan")
c3.metric("❌ Label Negatif",      f"{pct_neg}%",  f"{n_neg} ulasan", delta_color="inverse")
c4.metric("🤖 Akurasi Model",      f"{akurasi}%" if akurasi else "—",
          "vs label asli" if akurasi else "")

st.markdown("---")

# ── CHART ROW 1 ───────────────────────────────────────────────────────────────
cg1, cg2 = st.columns([1, 1.5])

with cg1:
    st.subheader("Distribusi Label Asli")
    pie_df = df["label"].value_counts().reset_index()
    pie_df.columns = ["Sentimen", "Jumlah"]
    fig_pie = px.pie(
        pie_df, names="Sentimen", values="Jumlah",
        color="Sentimen",
        color_discrete_map={"positif": C_POS, "negatif": C_NEG},
        hole=0.58,
    )
    fig_pie.update_traces(
        textinfo="percent+label", textfont_size=13,
        marker=dict(line=dict(color="#ffffff", width=3)),
    )
    fig_pie.update_layout(
        showlegend=True, height=270, margin=dict(t=5, b=5, l=5, r=5),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with cg2:
    st.subheader("Label Asli vs Prediksi Model")
    if "prediksi_model" in df.columns:
        perbandingan = pd.DataFrame({
            "Kategori": ["Label Asli", "Prediksi Model"],
            "Positif":  [
                (df["label"] == "positif").sum(),
                (df["prediksi_model"] == "positif").sum(),
            ],
            "Negatif": [
                (df["label"] == "negatif").sum(),
                (df["prediksi_model"] == "negatif").sum(),
            ],
        })
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="Positif", x=perbandingan["Kategori"],
                                  y=perbandingan["Positif"], marker_color=C_POS,
                                  text=perbandingan["Positif"], textposition="outside"))
        fig_bar.add_trace(go.Bar(name="Negatif", x=perbandingan["Kategori"],
                                  y=perbandingan["Negatif"], marker_color=C_NEG,
                                  text=perbandingan["Negatif"], textposition="outside"))
        fig_bar.update_layout(
            barmode="group", height=270, margin=dict(t=10, b=10, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=True, gridcolor="#e0ddd6"),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Kolom 'prediksi_model' tidak ditemukan.")

st.markdown("---")

# ── TREN WAKTU ────────────────────────────────────────────────────────────────
st.subheader("📈 Tren Ulasan per Periode Waktu")
tren_df = (
    df.groupby(["waktu", "waktu_urut", "label"])
    .size()
    .reset_index(name="n")
    .sort_values("waktu_urut", ascending=False)
)
tren_pivot = tren_df.pivot_table(index=["waktu","waktu_urut"], columns="label", values="n", fill_value=0).reset_index()
tren_pivot = tren_pivot.sort_values("waktu_urut", ascending=False)

fig_tren = go.Figure()
if "positif" in tren_pivot.columns:
    fig_tren.add_trace(go.Scatter(
        x=tren_pivot["waktu"], y=tren_pivot["positif"],
        name="Positif", mode="lines+markers",
        line=dict(color=C_POS, width=2), marker=dict(size=6),
    ))
if "negatif" in tren_pivot.columns:
    fig_tren.add_trace(go.Scatter(
        x=tren_pivot["waktu"], y=tren_pivot["negatif"],
        name="Negatif", mode="lines+markers",
        line=dict(color=C_NEG, width=2, dash="dot"), marker=dict(size=6),
    ))
fig_tren.update_layout(
    height=260, margin=dict(t=10, b=10, l=0, r=0),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, tickangle=-35),
    yaxis=dict(showgrid=True, gridcolor="#e0ddd6", title="Jumlah Ulasan"),
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
)
st.plotly_chart(fig_tren, use_container_width=True)

st.markdown("---")

# ── WORD CLOUD ────────────────────────────────────────────────────────────────
def buat_wc(teks_series, cmap, label):
    teks = " ".join(teks_series.dropna().tolist()).strip()
    if not teks:
        st.info(f"Tidak ada data {label}.")
        return
    wc = WordCloud(
        width=700, height=320,
        background_color=None, mode="RGBA",
        colormap=cmap, max_words=80,
        prefer_horizontal=0.85, collocations=False,
        min_font_size=10,
    ).generate(teks)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0)
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

wc1, wc2 = st.columns(2)
with wc1:
    st.subheader("☁️ Kata Populer — Ulasan Positif")
    buat_wc(df[df["label"] == "positif"]["clean_text"], "Greens", "positif")

with wc2:
    st.subheader("☁️ Kata Populer — Ulasan Negatif")
    buat_wc(df[df["label"] == "negatif"]["clean_text"], "Reds", "negatif")

st.markdown("---")

# ── CONFUSION MATRIX SEDERHANA ────────────────────────────────────────────────
if "prediksi_model" in df.columns and total:
    st.subheader("🎯 Confusion Matrix Model")
    tp = ((df["label"]=="positif") & (df["prediksi_model"]=="positif")).sum()
    fp = ((df["label"]=="negatif") & (df["prediksi_model"]=="positif")).sum()
    fn = ((df["label"]=="positif") & (df["prediksi_model"]=="negatif")).sum()
    tn = ((df["label"]=="negatif") & (df["prediksi_model"]=="negatif")).sum()

    z  = [[tn, fp], [fn, tp]]
    x_labels = ["Prediksi: Negatif", "Prediksi: Positif"]
    y_labels = ["Label: Negatif", "Label: Positif"]

    fig_cm = go.Figure(go.Heatmap(
        z=z, x=x_labels, y=y_labels,
        text=[[str(v) for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=18, color="white"),
        colorscale=[[0,"#C0392B"],[0.5,"#E67E22"],[1,"#1D9E75"]],
        showscale=False,
    ))
    fig_cm.update_layout(
        height=260, margin=dict(t=10, b=10, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(side="bottom"),
    )
    col_cm, col_info = st.columns([1.2, 1])
    with col_cm:
        st.plotly_chart(fig_cm, use_container_width=True)
    with col_info:
        prec = round(tp / (tp + fp) * 100, 1) if (tp + fp) else 0
        rec  = round(tp / (tp + fn) * 100, 1) if (tp + fn) else 0
        f1   = round(2 * prec * rec / (prec + rec), 1) if (prec + rec) else 0
        st.markdown(f"""
        | Metrik | Nilai |
        |--------|-------|
        | **Akurasi** | {akurasi}% |
        | **Presisi** | {prec}% |
        | **Recall** | {rec}% |
        | **F1-Score** | {f1}% |
        | **True Positive** | {tp} |
        | **True Negative** | {tn} |
        | **False Positive** | {fp} |
        | **False Negative** | {fn} |
        """)

    st.markdown("---")

# ── TABEL DATA ────────────────────────────────────────────────────────────────
st.subheader("📄 Data Ulasan Pengunjung")

search_q = st.text_input("🔍 Cari ulasan...", placeholder="ketik kata kunci...")
df_view = df.copy()
if search_q:
    df_view = df_view[df_view["review"].str.contains(search_q, case=False, na=False)]

# Pilih kolom yang ditampilkan
cols = ["user", "waktu", "review", "label"]
if show_pred and "prediksi_model" in df_view.columns:
    cols.append("prediksi_model")

df_display = df_view[cols].copy()

def warna_sentimen(val):
    if val == "positif":
        return "background-color:#e1f5ee;color:#085041;border-radius:20px;font-weight:500;"
    elif val == "negatif":
        return "background-color:#faece7;color:#993c1d;border-radius:20px;font-weight:500;"
    return ""

styled = df_display.style.applymap(
    warna_sentimen,
    subset=[c for c in ["label","prediksi_model"] if c in df_display.columns]
)

st.dataframe(styled, use_container_width=True, height=380)
st.caption(f"Menampilkan {len(df_view):,} dari {len(df):,} ulasan")

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Unduh Data Terfilter (CSV)",
    data=df_view.to_csv(index=False).encode("utf-8"),
    file_name="ulasan_kelud_filtered.csv",
    mime="text/csv",
)