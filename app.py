import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentimen Kelud",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DESIGN TOKENS & CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

/* ── Base reset ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #1a1210 !important;
    color: #e8e0d4 !important;
}

/* ── Headings ── */
h1, h2, h3, h4,
.stSubheader, [data-testid="stSubheader"] {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: -0.02em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #120e0c !important;
    border-right: 1px solid #2e241e !important;
}
[data-testid="stSidebar"] * {
    color: #c8bfb4 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stToggle label {
    color: #9b9189 !important;
    font-size: 12px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #241c18 !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem !important;
    border: 1px solid #3a2e27 !important;
    transition: border-color 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: #E8722A !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #9b9189 !important;
    font-weight: 600 !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Sora', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #f5f0e8 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 12px !important;
}

/* ── Plotly chart containers ── */
[data-testid="stPlotlyChart"] {
    background: #241c18 !important;
    border-radius: 16px !important;
    border: 1px solid #3a2e27 !important;
    padding: 0.5rem !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    background: #241c18 !important;
    border-radius: 16px !important;
    border: 1px solid #3a2e27 !important;
    overflow: hidden !important;
}
.stDataFrame thead tr th {
    background: #1a1210 !important;
    color: #9b9189 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Text input (search) ── */
[data-testid="stTextInput"] input {
    background: #241c18 !important;
    border: 1px solid #3a2e27 !important;
    border-radius: 10px !important;
    color: #e8e0d4 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #E8722A !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(232,114,42,0.15) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #E8722A !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.4rem !important;
    transition: background 0.2s, transform 0.1s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #cf5e1e !important;
    transform: translateY(-1px) !important;
}

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid #2e241e !important;
    margin: 1.5rem 0 !important;
}

/* ── Selectbox / multiselect ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #241c18 !important;
    border: 1px solid #3a2e27 !important;
    border-radius: 10px !important;
    color: #e8e0d4 !important;
}

/* ── Caption / small text ── */
.stCaption, [data-testid="stCaption"] {
    color: #6b6157 !important;
    font-size: 12px !important;
}

/* ── Subheader spacing ── */
[data-testid="stSubheader"] {
    margin-top: 0.25rem !important;
    margin-bottom: 0.75rem !important;
}

/* ── Image (wordcloud) container ── */
[data-testid="stImage"] {
    background: #241c18 !important;
    border-radius: 16px !important;
    border: 1px solid #3a2e27 !important;
    padding: 0.75rem !important;
    overflow: hidden;
}

/* ── Info boxes ── */
[data-testid="stInfo"] {
    background: #241c18 !important;
    border: 1px solid #3a2e27 !important;
    border-left: 3px solid #E8722A !important;
    border-radius: 10px !important;
    color: #c8bfb4 !important;
}

/* ── Table in markdown ── */
.stMarkdown table {
    border-collapse: collapse !important;
    width: 100%;
}
.stMarkdown th, .stMarkdown td {
    border: 1px solid #3a2e27 !important;
    padding: 8px 12px !important;
    color: #c8bfb4 !important;
    font-size: 13px !important;
}
.stMarkdown th {
    background: #2e241e !important;
    color: #9b9189 !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
    letter-spacing: 0.05em !important;
}
.stMarkdown tr:nth-child(even) td { background: #1e1713 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1a1210; }
::-webkit-scrollbar-thumb { background: #3a2e27; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #E8722A; }
</style>
""", unsafe_allow_html=True)

# ── PALETTE ───────────────────────────────────────────────────────────────────
C_POS      = "#2A9D5C"   # moss green
C_NEG      = "#C0392B"   # crater red
C_ACCENT   = "#E8722A"   # lava amber
C_BG       = "#241c18"
C_GRID     = "#2e241e"
C_TEXT     = "#e8e0d4"
C_MUTED    = "#9b9189"
PAPER_BG   = "rgba(0,0,0,0)"

def plotly_base():
    return dict(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PAPER_BG,
        font=dict(family="Inter, sans-serif", color=C_TEXT, size=12),
        margin=dict(t=16, b=16, l=8, r=8),
    )

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("dataset_kelud_final_prediction.csv")
    df.columns = df.columns.str.strip().str.lower()

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
    # Topographic accent
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(232,114,42,0.13) 0%, rgba(192,57,43,0.07) 50%, transparent 100%);
        border-radius: 12px;
        padding: 1.2rem 1rem 0.8rem;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(232,114,42,0.2);
    ">
        <div style="font-family:sans-serif;font-size:18px;font-weight:800;
                    color:#ffffff;letter-spacing:-0.02em;line-height:1.2;">
            🌋 Kelud
        </div>
        <div style="font-size:11px;color:#a09488;text-transform:uppercase;
                    letter-spacing:0.08em;margin-top:4px;font-weight:600;">
            Sentiment Explorer
        </div>
    </div>
    """, unsafe_allow_html=True)

    grup_opts = ["Semua"] + sorted(df_all["grup_waktu"].unique())
    grup_sel = st.selectbox("Periode Waktu", grup_opts)

    sentimen_sel = st.multiselect(
        "Sentimen (Label Asli)",
        ["positif", "negatif"],
        default=["positif", "negatif"],
    )

    show_pred = st.toggle("Tampilkan kolom Prediksi Model", value=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#4a403a;line-height:1.7;text-align:center;">
        Dashboard Sentimen Wisata<br>
        <span style="color:#6b5f57;">Gunung Kelud © 2025</span>
    </div>
    """, unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────────
df = df_all.copy()
if grup_sel != "Semua":
    df = df[df["grup_waktu"] == grup_sel]
if sentimen_sel:
    df = df[df["label"].isin(sentimen_sel)]

# ── HEADER ───────────────────────────────────────────────────────────────────
import streamlit.components.v1 as components

_n_all = len(df_all)
_n_df  = len(df)
_grup  = grup_sel

_header_html = f"""
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<div style="background:linear-gradient(135deg,#2e1f18 0%,#1e1410 60%,#1a1210 100%);border:1px solid #3a2e27;border-radius:20px;padding:2rem 2.25rem;position:relative;overflow:hidden;font-family:Inter,sans-serif;">
  <svg style="position:absolute;right:0;top:0;opacity:0.07;width:280px;height:160px;" viewBox="0 0 280 160" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="240" cy="80" rx="200" ry="60" stroke="#E8722A" stroke-width="1.5" fill="none"/>
    <ellipse cx="240" cy="80" rx="160" ry="46" stroke="#E8722A" stroke-width="1.5" fill="none"/>
    <ellipse cx="240" cy="80" rx="120" ry="33" stroke="#E8722A" stroke-width="1.5" fill="none"/>
    <ellipse cx="240" cy="80" rx="82"  ry="22" stroke="#E8722A" stroke-width="1.5" fill="none"/>
    <ellipse cx="240" cy="80" rx="48"  ry="13" stroke="#E8722A" stroke-width="1.5" fill="none"/>
    <ellipse cx="240" cy="80" rx="22"  ry="6"  stroke="#E8722A" stroke-width="1.5" fill="none"/>
  </svg>
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
    <div>
      <div style="font-family:Sora,sans-serif;font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.03em;line-height:1.15;">
        Dashboard Sentimen<br>
        <span style="color:#FF8C42;">Wisata Gunung Kelud</span>
      </div>
      <div style="margin-top:10px;font-size:13px;color:#c8bfb4;font-weight:500;">
        Analisis ulasan pengunjung &nbsp;&middot;&nbsp; {_n_all:,} total data
      </div>
    </div>
    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
      <div style="background:rgba(232,114,42,0.12);border:1px solid rgba(232,114,42,0.4);border-radius:30px;padding:6px 18px;font-size:12px;font-weight:600;color:#FF8C42;">
        🔥 {_n_df:,} ulasan ditampilkan
      </div>
      <div style="background:rgba(42,157,92,0.12);border:1px solid rgba(42,157,92,0.4);border-radius:30px;padding:6px 18px;font-size:12px;font-weight:600;color:#2ecc90;">
        📍 {_grup}
      </div>
    </div>
  </div>
</div>
"""
components.html(_header_html, height=148, scrolling=False)


# ── METRIK ────────────────────────────────────────────────────────────────────
total   = len(df)
n_pos   = (df["label"] == "positif").sum()
n_neg   = (df["label"] == "negatif").sum()
pct_pos = round(n_pos / total * 100) if total else 0
pct_neg = round(n_neg / total * 100) if total else 0

if "prediksi_model" in df.columns and total:
    benar   = (df["label"] == df["prediksi_model"]).sum()
    akurasi = round(benar / total * 100, 1)
else:
    akurasi = None

c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 Total Ulasan",   total)
c2.metric("✅ Positif",        f"{pct_pos}%",  f"{n_pos} ulasan")
c3.metric("❌ Negatif",        f"{pct_neg}%",  f"{n_neg} ulasan", delta_color="inverse")
c4.metric("🤖 Akurasi Model",  f"{akurasi}%" if akurasi else "—",
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
        hole=0.62,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        textfont=dict(size=13, family="Sora, sans-serif", color=C_TEXT),
        marker=dict(line=dict(color="#1a1210", width=3)),
    )
    fig_pie.update_layout(
        **plotly_base(),
        showlegend=True, height=280,
        legend=dict(
            orientation="h", y=-0.08, x=0.5, xanchor="center",
            font=dict(color=C_MUTED, size=12),
        ),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with cg2:
    st.subheader("Label Asli vs Prediksi Model")
    if "prediksi_model" in df.columns:
        perbandingan = pd.DataFrame({
            "Kategori": ["Label Asli", "Prediksi Model"],
            "Positif": [
                (df["label"] == "positif").sum(),
                (df["prediksi_model"] == "positif").sum(),
            ],
            "Negatif": [
                (df["label"] == "negatif").sum(),
                (df["prediksi_model"] == "negatif").sum(),
            ],
        })
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Positif", x=perbandingan["Kategori"],
            y=perbandingan["Positif"], marker_color=C_POS,
            marker=dict(cornerradius=6),
            text=perbandingan["Positif"], textposition="outside",
            textfont=dict(color=C_TEXT, size=12, family="Sora"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Negatif", x=perbandingan["Kategori"],
            y=perbandingan["Negatif"], marker_color=C_NEG,
            marker=dict(cornerradius=6),
            text=perbandingan["Negatif"], textposition="outside",
            textfont=dict(color=C_TEXT, size=12, family="Sora"),
        ))
        fig_bar.update_layout(
            **plotly_base(),
            barmode="group", height=280,
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color=C_MUTED, size=12, family="Sora"),
                linecolor=C_GRID,
            ),
            yaxis=dict(
                showgrid=True, gridcolor=C_GRID,
                tickfont=dict(color=C_MUTED, size=11),
                title=dict(text="Jumlah Ulasan", font=dict(color=C_MUTED, size=11)),
            ),
            legend=dict(
                orientation="h", y=-0.12, x=0.5, xanchor="center",
                font=dict(color=C_MUTED, size=12),
            ),
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
tren_pivot = (
    tren_df.pivot_table(index=["waktu","waktu_urut"], columns="label", values="n", fill_value=0)
    .reset_index()
    .sort_values("waktu_urut", ascending=False)
)

fig_tren = go.Figure()
if "positif" in tren_pivot.columns:
    fig_tren.add_trace(go.Scatter(
        x=tren_pivot["waktu"], y=tren_pivot["positif"],
        name="Positif", mode="lines+markers",
        line=dict(color=C_POS, width=2.5),
        marker=dict(size=7, color=C_POS, line=dict(color="#1a1210", width=2)),
        fill="tozeroy",
        fillcolor=f"rgba(42,157,92,0.08)",
    ))
if "negatif" in tren_pivot.columns:
    fig_tren.add_trace(go.Scatter(
        x=tren_pivot["waktu"], y=tren_pivot["negatif"],
        name="Negatif", mode="lines+markers",
        line=dict(color=C_NEG, width=2.5, dash="dot"),
        marker=dict(size=7, color=C_NEG, line=dict(color="#1a1210", width=2)),
        fill="tozeroy",
        fillcolor=f"rgba(192,57,43,0.07)",
    ))
fig_tren.update_layout(
    **plotly_base(),
    height=280,
    xaxis=dict(
        showgrid=False, tickangle=-35,
        tickfont=dict(color=C_MUTED, size=11),
        linecolor=C_GRID,
    ),
    yaxis=dict(
        showgrid=True, gridcolor=C_GRID,
        tickfont=dict(color=C_MUTED, size=11),
        title=dict(text="Jumlah Ulasan", font=dict(color=C_MUTED, size=11)),
    ),
    legend=dict(
        orientation="h", y=-0.22, x=0.5, xanchor="center",
        font=dict(color=C_MUTED, size=12),
    ),
    hovermode="x unified",
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
        width=720, height=340,
        background_color=None, mode="RGBA",
        colormap=cmap, max_words=90,
        prefer_horizontal=0.82, collocations=False,
        min_font_size=11,
        font_step=1,
    ).generate(teks)
    fig, ax = plt.subplots(figsize=(7.2, 3.4), facecolor="none")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0)
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=130)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

wc1, wc2 = st.columns(2)
with wc1:
    st.subheader("☁️ Kata Populer — Positif")
    buat_wc(df[df["label"] == "positif"]["clean_text"], "YlGn", "positif")

with wc2:
    st.subheader("☁️ Kata Populer — Negatif")
    buat_wc(df[df["label"] == "negatif"]["clean_text"], "OrRd", "negatif")

st.markdown("---")

# ── CONFUSION MATRIX ────────────────────────────────────────────────────────
if "prediksi_model" in df.columns and total:
    st.subheader("🎯 Confusion Matrix Model")

    tp = ((df["label"]=="positif") & (df["prediksi_model"]=="positif")).sum()
    fp = ((df["label"]=="negatif") & (df["prediksi_model"]=="positif")).sum()
    fn = ((df["label"]=="positif") & (df["prediksi_model"]=="negatif")).sum()
    tn = ((df["label"]=="negatif") & (df["prediksi_model"]=="negatif")).sum()

    z         = [[tn, fp], [fn, tp]]
    x_labels  = ["Prediksi: Negatif", "Prediksi: Positif"]
    y_labels  = ["Label: Negatif", "Label: Positif"]

    fig_cm = go.Figure(go.Heatmap(
        z=z, x=x_labels, y=y_labels,
        text=[[str(v) for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(size=20, color="white", family="Sora"),
        colorscale=[[0, C_NEG], [0.5, "#E8722A"], [1, C_POS]],
        showscale=False,
    ))
    fig_cm.update_layout(
        **plotly_base(),
        height=270,
        xaxis=dict(side="bottom", tickfont=dict(color=C_MUTED, size=12, family="Sora")),
        yaxis=dict(tickfont=dict(color=C_MUTED, size=12, family="Sora")),
    )

    col_cm, col_info = st.columns([1.2, 1])
    with col_cm:
        st.plotly_chart(fig_cm, use_container_width=True)
    with col_info:
        prec = round(tp / (tp + fp) * 100, 1) if (tp + fp) else 0
        rec  = round(tp / (tp + fn) * 100, 1) if (tp + fn) else 0
        f1   = round(2 * prec * rec / (prec + rec), 1) if (prec + rec) else 0

        # Custom styled metric cards for model stats
        def stat_card(label, value, color="#e8e0d4"):
            return f"""
            <div style="
                background:#241c18;border:1px solid #3a2e27;border-radius:12px;
                padding:12px 16px;margin-bottom:8px;
                display:flex;align-items:center;justify-content:space-between;
            ">
                <span style="font-size:12px;color:#9b9189;font-family:'Inter',sans-serif;
                             text-transform:uppercase;letter-spacing:0.06em;font-weight:600;">
                    {label}
                </span>
                <span style="font-size:18px;font-weight:700;color:{color};
                             font-family:'Sora',sans-serif;">
                    {value}
                </span>
            </div>
            """

        st.markdown(
            stat_card("Akurasi",       f"{akurasi}%",  "#E8722A") +
            stat_card("Presisi",        f"{prec}%",     C_POS) +
            stat_card("Recall",         f"{rec}%",      C_POS) +
            stat_card("F1-Score",       f"{f1}%",       C_POS) +
            stat_card("True Positive",  str(tp)) +
            stat_card("True Negative",  str(tn)) +
            stat_card("False Positive", str(fp), C_NEG) +
            stat_card("False Negative", str(fn), C_NEG),
            unsafe_allow_html=True
        )

    st.markdown("---")

# ── TABEL DATA ────────────────────────────────────────────────────────────────
st.subheader("📄 Data Ulasan Pengunjung")

search_q = st.text_input("🔍 Cari ulasan...", placeholder="Ketik kata kunci untuk memfilter...")
df_view  = df.copy()
if search_q:
    df_view = df_view[df_view["review"].str.contains(search_q, case=False, na=False)]

cols = ["user", "waktu", "review", "label"]
if show_pred and "prediksi_model" in df_view.columns:
    cols.append("prediksi_model")

df_display = df_view[cols].copy()

def warna_sentimen(val):
    if val == "positif":
        return "background-color:#0d2e1e;color:#2ecc90;border-radius:4px;font-weight:600;font-size:12px;"
    elif val == "negatif":
        return "background-color:#2e0d0d;color:#e05c5c;border-radius:4px;font-weight:600;font-size:12px;"
    return ""

styled = df_display.style.map(
    warna_sentimen,
    subset=[c for c in ["label", "prediksi_model"] if c in df_display.columns],
)

st.dataframe(styled, use_container_width=True, height=400)
st.caption(f"Menampilkan {len(df_view):,} dari {len(df):,} ulasan")

st.markdown("<br>", unsafe_allow_html=True)

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Unduh Data Terfilter (CSV)",
    data=df_view.to_csv(index=False).encode("utf-8"),
    file_name="ulasan_kelud_filtered.csv",
    mime="text/csv",
)