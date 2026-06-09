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
    background-color: #0A0A0A !important; /* Deep Black */
    color: #F0F0F0 !important; /* Crisp White */
}

/* ── Headings ── */
h1, h2, h3, h4,
.stSubheader, [data-testid="stSubheader"] {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #110E0E !important; /* Very dark maroon tint */
    border-right: 1px solid #2E1A1A !important;
}
[data-testid="stSidebar"] * {
    color: #D4C9C9 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stToggle label {
    color: #A38C8C !important;
    font-size: 12px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #171212 !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
    border: 1px solid #3D2626 !important;
    transition: all 0.3s ease;
}
[data-testid="metric-container"]:hover {
    border-color: #D32F2F !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(211, 47, 47, 0.15);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #B5A1A1 !important;
    font-weight: 600 !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Sora', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
}

/* ── Plotly chart containers ── */
[data-testid="stPlotlyChart"] {
    background: #171212 !important;
    border-radius: 12px !important;
    border: 1px solid #3D2626 !important;
    padding: 0.5rem !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    background: #171212 !important;
    border-radius: 12px !important;
    border: 1px solid #3D2626 !important;
    overflow: hidden !important;
}
.stDataFrame thead tr th {
    background: #0A0A0A !important;
    color: #B5A1A1 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Text input (search) ── */
[data-testid="stTextInput"] input {
    background: #171212 !important;
    border: 1px solid #3D2626 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #D32F2F !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(211, 47, 47, 0.2) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #8B0000 !important; /* Maroon */
    color: #fff !important;
    border: 1px solid #A50000 !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #B30000 !important;
    border-color: #FF3D3D !important;
    transform: translateY(-1px) !important;
}

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid #2E1A1A !important;
    margin: 1.5rem 0 !important;
}

/* ── Selectbox / multiselect ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #171212 !important;
    border: 1px solid #3D2626 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}

/* ── Info boxes ── */
[data-testid="stInfo"] {
    background: #171212 !important;
    border: 1px solid #3D2626 !important;
    border-left: 4px solid #D32F2F !important;
    border-radius: 8px !important;
    color: #F0F0F0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0A0A0A; }
::-webkit-scrollbar-thumb { background: #3D2626; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #D32F2F; }
</style>
""", unsafe_allow_html=True)

# ── PALETTE ───────────────────────────────────────────────────────────────────
C_POS      = "#00E676"   # Bright Neon Green for clarity
C_NEG      = "#FF3D00"   # Vibrant Red-Orange for clarity
C_ACCENT   = "#D32F2F"   # Strong Crimson/Maroon Accent
C_BG       = "#0A0A0A"
C_GRID     = "#2E1A1A"
C_TEXT     = "#FFFFFF"
C_MUTED    = "#A38C8C"
PAPER_BG   = "rgba(0,0,0,0)"

def plotly_base():
    return dict(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PAPER_BG,
        font=dict(family="Inter, sans-serif", color=C_TEXT, size=12),
        margin=dict(t=24, b=24, l=12, r=12),
    )

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("kelud_final.csv")
        df.columns = df.columns.str.strip().str.lower()
    except FileNotFoundError:
        # Dummy data untuk mencegah error jika file tidak ada saat testing
        df = pd.DataFrame({
            "waktu": ["hari ini", "minggu lalu", "sebulan lalu", "setahun lalu"],
            "label": ["positif", "negatif", "positif", "positif"],
            "prediksi_model": ["positif", "negatif", "negatif", "positif"],
            "review": ["Bagus banget", "Jelek, kotor", "Pemandangan indah", "Lumayan"],
            "clean_text": ["bagus banget", "jelek kotor", "pemandang indah", "lumayan"]
        })

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
    
    if "waktu" in df.columns:
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
    else:
        df["grup_waktu"] = "Unknown"
        df["waktu_urut"] = 0
        
    return df

df_all = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #8B000033 0%, #1A0A0A 100%);
        border-radius: 10px;
        padding: 1.5rem 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid #3D2626;
        text-align: center;
    ">
        <div style="font-family:'Sora',sans-serif;font-size:22px;font-weight:800;
                    color:#FFFFFF;letter-spacing:-0.02em;line-height:1.2;">
            🌋 KELUD
        </div>
        <div style="font-size:12px;color:#D32F2F;text-transform:uppercase;
                    letter-spacing:0.1em;margin-top:6px;font-weight:700;">
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

    show_pred = st.toggle("Tampilkan kolom Prediksi", value=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#7A6A6A;line-height:1.7;text-align:center;">
        Dashboard Sentimen Wisata<br>
        <span style="color:#A38C8C; font-weight:600;">Gunung Kelud © 2026</span>
    </div>
    """, unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────────
df = df_all.copy()
if grup_sel != "Semua":
    df = df[df["grup_waktu"] == grup_sel]
if sentimen_sel:
    df = df[df["label"].isin(sentimen_sel)]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #2b1111 0%, #170b0b 50%, #0A0A0A 100%);
    border: 1px solid #3D2626;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
">
    <svg style="position:absolute;right:-20px;top:-20px;opacity:0.15;width:300px;height:200px;"
         viewBox="0 0 280 160" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="240" cy="80" rx="200" ry="60" stroke="#D32F2F" stroke-width="2" fill="none"/>
        <ellipse cx="240" cy="80" rx="160" ry="46" stroke="#D32F2F" stroke-width="2" fill="none"/>
        <ellipse cx="240" cy="80" rx="120" ry="33" stroke="#D32F2F" stroke-width="2" fill="none"/>
        <ellipse cx="240" cy="80" rx="82" ry="22" stroke="#D32F2F" stroke-width="2" fill="none"/>
    </svg>

    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1.5rem; position:relative; z-index:1;">
        <div>
            <div style="
                font-family:'Sora',sans-serif;
                font-size:32px;font-weight:800;
                color:#FFFFFF;
                letter-spacing:-0.02em;line-height:1.2;
            ">Dashboard Sentimen<br>
                <span style="color:#D32F2F;">Wisata Gunung Kelud</span>
            </div>
            <div style="
                margin-top:12px;font-size:14px;color:#A38C8C;
                font-family:'Inter',sans-serif;font-weight:500;
            ">
                Analisis ulasan pengunjung &nbsp;·&nbsp; <strong style="color:#FFF;">{len(df_all):,}</strong> total data
            </div>
        </div>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
            <div style="
                background:rgba(211, 47, 47, 0.1);border:1px solid rgba(211, 47, 47, 0.4);
                border-radius:30px;padding:8px 20px;
                font-size:13px;font-weight:700;color:#FF5252;
                font-family:'Sora',sans-serif;
            ">🔥 {len(df):,} ulasan aktif</div>
            <div style="
                background:rgba(255, 255, 255, 0.05);border:1px solid rgba(255, 255, 255, 0.15);
                border-radius:30px;padding:8px 20px;
                font-size:13px;font-weight:700;color:#E0E0E0;
                font-family:'Sora',sans-serif;
            ">📍 {grup_sel}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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
c4.metric("🤖 Akurasi Model",  f"{akurasi}%" if akurasi else "—", "vs label asli" if akurasi else "")

st.markdown("---")

# ── CHART ROW 1 ───────────────────────────────────────────────────────────────
cg1, cg2 = st.columns([1, 1.5])

with cg1:
    st.subheader("Distribusi Label")
    pie_df = df["label"].value_counts().reset_index()
    pie_df.columns = ["Sentimen", "Jumlah"]
    fig_pie = px.pie(
        pie_df, names="Sentimen", values="Jumlah",
        color="Sentimen",
        color_discrete_map={"positif": C_POS, "negatif": C_NEG},
        hole=0.65,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        textfont=dict(size=14, family="Sora, sans-serif", color="#FFF"),
        marker=dict(line=dict(color="#0A0A0A", width=4)),
    )
    fig_pie.update_layout(
        **plotly_base(),
        showlegend=False, height=320,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with cg2:
    st.subheader("Label Asli vs Prediksi")
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
            marker=dict(cornerradius=4),
            text=perbandingan["Positif"], textposition="outside",
            textfont=dict(color="#FFF", size=13, family="Sora"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Negatif", x=perbandingan["Kategori"],
            y=perbandingan["Negatif"], marker_color=C_NEG,
            marker=dict(cornerradius=4),
            text=perbandingan["Negatif"], textposition="outside",
            textfont=dict(color="#FFF", size=13, family="Sora"),
        ))
        fig_bar.update_layout(
            **plotly_base(),
            barmode="group", height=320,
            xaxis=dict(showgrid=False, tickfont=dict(color=C_MUTED, size=13, family="Sora"), linecolor=C_GRID),
            yaxis=dict(showgrid=True, gridcolor=C_GRID, tickfont=dict(color=C_MUTED, size=11), title=dict(text="Jumlah Ulasan", font=dict(color=C_MUTED))),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(color="#FFF", size=13)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Kolom 'prediksi_model' tidak ditemukan.")

st.markdown("---")

# ── TREN WAKTU ────────────────────────────────────────────────────────────────
if "waktu" in df.columns:
    st.subheader("📈 Tren Ulasan Waktu")
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
            line=dict(color=C_POS, width=3),
            marker=dict(size=8, color=C_POS, line=dict(color="#0A0A0A", width=2)),
            fill="tozeroy", fillcolor=f"rgba(0, 230, 118, 0.05)",
        ))
    if "negatif" in tren_pivot.columns:
        fig_tren.add_trace(go.Scatter(
            x=tren_pivot["waktu"], y=tren_pivot["negatif"],
            name="Negatif", mode="lines+markers",
            line=dict(color=C_NEG, width=3, dash="solid"),
            marker=dict(size=8, color=C_NEG, line=dict(color="#0A0A0A", width=2)),
            fill="tozeroy", fillcolor=f"rgba(255, 61, 0, 0.05)",
        ))
    fig_tren.update_layout(
        **plotly_base(), height=320,
        xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(color=C_MUTED, size=12), linecolor=C_GRID),
        yaxis=dict(showgrid=True, gridcolor=C_GRID, tickfont=dict(color=C_MUTED, size=11)),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(color="#FFF", size=13)),
        hovermode="x unified",
    )
    st.plotly_chart(fig_tren, use_container_width=True)
    st.markdown("---")

# ── WORD CLOUD ────────────────────────────────────────────────────────────────
if "clean_text" in df.columns:
    def buat_wc(teks_series, cmap, label):
        teks = " ".join(teks_series.dropna().tolist()).strip()
        if not teks:
            st.info(f"Tidak ada data {label}.")
            return
        wc = WordCloud(
            width=800, height=400,
            background_color=None, mode="RGBA",
            colormap=cmap, max_words=80,
            prefer_horizontal=0.85, collocations=False,
            font_step=2,
        ).generate(teks)
        fig, ax = plt.subplots(figsize=(8, 4), facecolor="none")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        fig.patch.set_alpha(0)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=150)
        buf.seek(0)
        st.image(buf, use_container_width=True)
        plt.close(fig)

    wc1, wc2 = st.columns(2)
    with wc1:
        st.subheader("☁️ Kata Positif")
        buat_wc(df[df["label"] == "positif"]["clean_text"], "Greens", "positif")

    with wc2:
        st.subheader("☁️ Kata Negatif")
        buat_wc(df[df["label"] == "negatif"]["clean_text"], "Reds", "negatif")

    st.markdown("---")

# ── CONFUSION MATRIX ────────────────────────────────────────────────────────
if "prediksi_model" in df.columns and total:
    st.subheader("🎯 Performa Model Klasifikasi")

    tp = ((df["label"]=="positif") & (df["prediksi_model"]=="positif")).sum()
    fp = ((df["label"]=="negatif") & (df["prediksi_model"]=="positif")).sum()
    fn = ((df["label"]=="positif") & (df["prediksi_model"]=="negatif")).sum()
    tn = ((df["label"]=="negatif") & (df["prediksi_model"]=="negatif")).sum()

    z         = [[tn, fp], [fn, tp]]
    x_labels  = ["Prediksi Negatif", "Prediksi Positif"]
    y_labels  = ["Aktual Negatif", "Aktual Positif"]

    fig_cm = go.Figure(go.Heatmap(
        z=z, x=x_labels, y=y_labels,
        text=[[str(v) for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(size=24, color="white", family="Sora"),
        colorscale=[[0, "#170B0B"], [0.5, "#8B0000"], [1, "#D32F2F"]], # Maroon Gradient
        showscale=False,
    ))
    fig_cm.update_layout(
        **plotly_base(), height=300,
        xaxis=dict(side="bottom", tickfont=dict(color="#FFF", size=13, family="Sora")),
        yaxis=dict(tickfont=dict(color="#FFF", size=13, family="Sora")),
    )

    col_cm, col_info = st.columns([1.5, 1])
    with col_cm:
        st.plotly_chart(fig_cm, use_container_width=True)
    with col_info:
        prec = round(tp / (tp + fp) * 100, 1) if (tp + fp) else 0
        rec  = round(tp / (tp + fn) * 100, 1) if (tp + fn) else 0
        f1   = round(2 * prec * rec / (prec + rec), 1) if (prec + rec) else 0

        def stat_card(label, value, color="#FFF"):
            return f"""
            <div style="
                background:#171212;border:1px solid #3D2626;border-radius:8px;
                padding:10px 16px;margin-bottom:8px;
                display:flex;align-items:center;justify-content:space-between;
            ">
                <span style="font-size:12px;color:#A38C8C;font-family:'Inter',sans-serif;
                             text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">
                    {label}
                </span>
                <span style="font-size:18px;font-weight:800;color:{color};
                             font-family:'Sora',sans-serif;">
                    {value}
                </span>
            </div>
            """

        st.markdown(
            stat_card("Akurasi",       f"{akurasi}%",  "#D32F2F") +
            stat_card("Presisi",        f"{prec}%",     C_POS) +
            stat_card("Recall",         f"{rec}%",      C_POS) +
            stat_card("F1-Score",       f"{f1}%",       C_POS) +
            stat_card("True Positive",  str(tp)) +
            stat_card("False Positive", str(fp),        C_NEG),
            unsafe_allow_html=True
        )

    st.markdown("---")

# ── TABEL DATA ────────────────────────────────────────────────────────────────
st.subheader("📄 Eksekusi Data Ulasan")

search_q = st.text_input("🔍 Cari ulasan...", placeholder="Ketik kata kunci untuk memfilter tabel...")
df_view  = df.copy()

if "review" in df_view.columns and search_q:
    df_view = df_view[df_view["review"].astype(str).str.contains(search_q, case=False, na=False)]

cols = [c for c in ["user", "waktu", "review", "label"] if c in df_view.columns]
if show_pred and "prediksi_model" in df_view.columns:
    cols.append("prediksi_model")

df_display = df_view[cols].copy()

def warna_sentimen(val):
    if val == "positif":
        return "background-color:#003314;color:#00E676;border-radius:4px;font-weight:700;font-size:12px;"
    elif val == "negatif":
        return "background-color:#330A00;color:#FF3D00;border-radius:4px;font-weight:700;font-size:12px;"
    return ""

styled = df_display.style.applymap(
    warna_sentimen,
    subset=[c for c in ["label", "prediksi_model"] if c in df_display.columns],
)

st.dataframe(styled, use_container_width=True, height=450)
st.caption(f"Menampilkan {len(df_view):,} dari total {len(df):,} ulasan aktif")

st.markdown("<br>", unsafe_allow_html=True)

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Unduh Data (CSV)",
    data=df_view.to_csv(index=False).encode("utf-8"),
    file_name="ulasan_kelud_filtered.csv",
    mime="text/csv",
)