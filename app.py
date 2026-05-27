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

# ── CSS CUSTOM (Modern Cyber & Clean Glassmorphism) ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Font Utama & Background */
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    background-color: #f8fafc;
}

/* Tipografi Judul */
h1, h2, h3 { 
    font-family: 'Inter', sans-serif !important; 
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #0f172a !important;
}

/* Glassmorphic Metric Cards */
[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
}

/* Sidebar Styling */
[data-testid="stSidebar"] { 
    background-color: #0f172a !important; 
    color: #f8fafc !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
    color: #f8fafc !important;
}

/* DataFrame Custom */
.stDataFrame { 
    border-radius: 10px; 
    overflow: hidden; 
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

/* Garis Pembatas Minimalis */
hr {
    margin: 1.5rem 0 !important;
    border: 0;
    border-top: 1px solid #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# Palet Warna Vibrant Neon
C_POS = "#10b981"  
C_NEG = "#ff4a4a"  
C_BG_TRACE = "rgba(0,0,0,0)"

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("kelud_final.csv")
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

# ── SIDEBAR (Dark Theme Accent) ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Control Panel")
    st.markdown("Filter & konfigurasikan visualisasi data.")
    st.markdown("---")

    grup_opts = ["Semua"] + sorted(df_all["grup_waktu"].unique())
    grup_sel = st.selectbox("🕒 Periode Waktu", grup_opts)

    sentimen_sel = st.multiselect(
        "💬 Sentimen Utama",
        ["positif", "negatif"],
        default=["positif", "negatif"],
    )

    show_pred = st.toggle("Tampilkan Prediksi Model", value=True)

    st.markdown("---")
    st.caption("Dashboard Sentimen Wisata\nGunung Kelud © 2026")

# ── FILTER LOGIC ──────────────────────────────────────────────────────────────
df = df_all.copy()
if grup_sel != "Semua":
    df = df[df["grup_waktu"] == grup_sel]
if sentimen_sel:
    df = df[df["label"].isin(sentimen_sel)]

# ── HEADER SECTION ────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;justify-content:between;margin-bottom:0.5rem;width:100%;">
  <div style="flex-grow:1;">
    <h1 style="margin:0;font-size:26px;color:#0f172a;font-weight:700;">🌋 DATA INTEL: SENTIMEN GUNUNG KELUD</h1>
    <p style="color:#64748b;font-size:14px;margin-top:2px;margin-bottom:0;">Hasil klasifikasi ulasan wisatawan menggunakan arsitektur pemrosesan bahasa alami</p>
  </div>
  <div style="text-align:right;">
    <span style="background:#0f172a;color:#f8fafc;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:600;letter-spacing:0.05em;">
      FILTERED: {:,} ROWS
    </span>
  </div>
</div>
""".format(len(df)), unsafe_allow_html=True)
st.markdown("---")

# ── METRICS ROW ───────────────────────────────────────────────────────────────
total = len(df)
n_pos = (df["label"] == "positif").sum()
n_neg = (df["label"] == "negatif").sum()
pct_pos = round(n_pos / total * 100) if total else 0
pct_neg = round(n_neg / total * 100) if total else 0

if "prediksi_model" in df.columns and total:
    benar = (df["label"] == df["prediksi_model"]).sum()
    akurasi = round(benar / total * 100, 1)
else:
    akurasi = None

m1, m2, m3, m4 = st.columns(4)
m1.metric("TOTAL DATASETS", f"{total:,}")
m2.metric("POSITIVE SENTIMENT", f"{pct_pos}%", f"+{n_pos:,} reviews")
m3.metric("NEGATIVE SENTIMENT", f"{pct_neg}%", f"-{n_neg:,} reviews", delta_color="inverse")
m4.metric("MODEL ACCURACY", f"{akurasi}%" if akurasi else "—", "validation rate" if akurasi else "")

st.markdown("---")

# ── GRAPHICS ROW 1 ────────────────────────────────────────────────────────────
cg1, cg2 = st.columns([1, 1.4])

with cg1:
    st.markdown("### 📊 Proporsi Distribusi Kelas")
    pie_df = df["label"].value_counts().reset_index()
    pie_df.columns = ["Sentimen", "Jumlah"]
    
    fig_pie = px.pie(
        pie_df, names="Sentimen", values="Jumlah",
        color="Sentimen",
        color_discrete_map={"positif": C_POS, "negatif": C_NEG},
        hole=0.7,
    )
    fig_pie.update_traces(
        textinfo="percent", font=dict(size=12, color="#ffffff", weight="bold"),
        marker=dict(line=dict(color="#f8fafc", width=3)),
    )
    fig_pie.update_layout(
        showlegend=True, height=270, margin=dict(t=15, b=15, l=10, r=10),
        paper_bgcolor=C_BG_TRACE,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(color="#475569", size=11)),
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

with cg2:
    st.markdown("### 🤖 Distribusi Aktual vs Prediksi Model")
    if "prediksi_model" in df.columns:
        perbandingan = pd.DataFrame({
            "Kategori": ["Aktual (Label)", "Prediksi Model"],
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
            name="Positif", x=perbandingan["Kategori"], y=perbandingan["Positif"], 
            marker_color=C_POS, text=perbandingan["Positif"], textposition="outside",
            marker_line_width=0, marker_corner_radius=4, textfont=dict(weight="bold")
        ))
        fig_bar.add_trace(go.Bar(
            name="Negatif", x=perbandingan["Kategori"], y=perbandingan["Negatif"], 
            marker_color=C_NEG, text=perbandingan["Negatif"], textposition="outside",
            marker_line_width=0, marker_corner_radius=4, textfont=dict(weight="bold")
        ))
        
        fig_bar.update_layout(
            barmode="group", height=270, margin=dict(t=30, b=15, l=0, r=0),
            paper_bgcolor=C_BG_TRACE, plot_bgcolor=C_BG_TRACE,
            yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False, showticklabels=False),
            xaxis=dict(zeroline=False),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(color="#475569", size=11)),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Fitur 'prediksi_model' absen di dalam berkas CSV.")

st.markdown("---")

# ── TIMELINE TRENDS ───────────────────────────────────────────────────────────
st.markdown("### 📈 Chronological Trend Analysis")
tren_df = (
    df.groupby(["waktu", "waktu_urut", "label"])
    .size()
    .reset_index(name="n")
)
tren_pivot = tren_df.pivot_table(index=["waktu","waktu_urut"], columns="label", values="n", fill_value=0).reset_index()
tren_pivot = tren_pivot.sort_values("waktu_urut", ascending=False)

fig_tren = go.Figure()
if "positif" in tren_pivot.columns:
    fig_tren.add_trace(go.Scatter(
        x=tren_pivot["waktu"], y=tren_pivot["positif"],
        name="Positif", mode="lines+markers",
        line=dict(color=C_POS, width=3), marker=dict(size=6, symbol="circle"),
    ))
if "negatif" in tren_pivot.columns:
    fig_tren.add_trace(go.Scatter(
        x=tren_pivot["waktu"], y=tren_pivot["negatif"],
        name="Negatif", mode="lines+markers",
        line=dict(color=C_NEG, width=2, dash="dash"), marker=dict(size=6, symbol="square"),
    ))

fig_tren.update_layout(
    height=270, margin=dict(t=15, b=15, l=0, r=0),
    paper_bgcolor=C_BG_TRACE, plot_bgcolor=C_BG_TRACE,
    xaxis=dict(showgrid=False, tickangle=0, font=dict(size=11, color="#64748b")),
    yaxis=dict(showgrid=True, gridcolor="#e2e8f0", title="Volume Ulasan", titlefont=dict(color="#64748b")),
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
)
st.plotly_chart(fig_tren, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ── WORD CLOUD FUNCTION ───────────────────────────────────────────────────────
def buat_wc(teks_series, cmap, label):
    teks = " ".join(teks_series.dropna().tolist()).strip()
    if not teks:
        st.info(f"Korpus kata {label} kosong.")
        return
    
    # Menggunakan background transparan dengan kontras tinggi
    wc = WordCloud(
        width=750, height=280,
        background_color=None, mode="RGBA",
        colormap=cmap, max_words=50,
        prefer_horizontal=1.0, collocations=False,
    ).generate(teks)
    
    fig, ax = plt.subplots(figsize=(7.5, 2.8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0)
    
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=300)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

wc1, wc2 = st.columns(2)
with wc1:
    st.markdown("### ☁️ Token Teratas: Sentimen Positif")
    buat_wc(df[df["label"] == "positif"]["clean_text"], "winter", "positif")

with wc2:
    st.markdown("### ☁️ Token Teratas: Sentimen Negatif")
    buat_wc(df[df["label"] == "negatif"]["clean_text"], "autumn", "negatif")

st.markdown("---")

# ── MATRIX PERFORMANCE ────────────────────────────────────────────────────────
if "prediksi_model" in df.columns and total:
    st.markdown("### 🎯 Confusion Matrix & Parameter Evaluasi Model")
    
    tp = ((df["label"]=="positif") & (df["prediksi_model"]=="positif")).sum()
    fp = ((df["label"]=="negatif") & (df["prediksi_model"]=="positif")).sum()
    fn = ((df["label"]=="positif") & (df["prediksi_model"]=="negatif")).sum()
    tn = ((df["label"]=="negatif") & (df["prediksi_model"]=="negatif")).sum()

    z = [[tn, fp], [fn, tp]]
    x_labels = ["Prediksi: NEGATIF", "Prediksi: POSITIF"]
    y_labels = ["Aktual: NEGATIF", "Aktual: POSITIF"]

    fig_cm = go.Figure(go.Heatmap(
        z=z, x=x_labels, y=y_labels,
        text=[[str(v) for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=15, color="#ffffff", weight="bold"),
        colorscale=[[0, "#334155"], [0.5, "#475569"], [1, "#0f172a"]],
        showscale=False,
    ))
    fig_cm.update_layout(
        height=250, margin=dict(t=10, b=10, l=0, r=0),
        paper_bgcolor=C_BG_TRACE, plot_bgcolor=C_BG_TRACE,
        xaxis=dict(side="bottom", zeroline=False), yaxis=dict(zeroline=False)
    )
    
    col_cm, col_info = st.columns([1, 1])
    with col_cm:
        st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
    with col_info:
        prec = round(tp / (tp + fp) * 100, 1) if (tp + fp) else 0
        rec  = round(tp / (tp + fn) * 100, 1) if (tp + fn) else 0
        f1   = round(2 * prec * rec / (prec + rec), 1) if (prec + rec) else 0
        
        st.markdown(f"""
        <div style="padding-top: 5px;">
        
        | Parameter Metrik | Hasil Klasifikasi |
        | :--- | :--- |
        | 🟢 **Accuracy** | `{akurasi}%` |
        | 🔵 **Precision** | `{prec}%` |
        | 🟡 **Recall** | `{rec}%` |
        | 🟣 **F1-Score** | `{f1}%` |
        
        <p style="font-size:12px; color:#64748b; margin-top:10px;">Struktur Data Matriks: True Positive ({tp}), True Negative ({tn}), False Positive ({fp}), False Negative ({fn}).</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

# ── EXPLORASI DATA ────────────────────────────────────────────────────────────
st.markdown("### 📄 Data Explorer")

col_search, col_dl = st.columns([3, 1])
with col_search:
    search_q = st.text_input("Gunakan filter teks kueri:", placeholder="Cari ulasan berdasarkan potongan kata kunci di sini...")
with col_dl:
    st.write("<div style='height:28px;'></div>", unsafe_allow_html=True)
    df_view = df.copy()
    if search_q:
        df_view = df_view[df_view["review"].str.contains(search_q, case=False, na=False)]
    
    st.download_button(
        "⚡ EXPORT TO CSV",
        data=df_view.to_csv(index=False).encode("utf-8"),
        file_name="ulasan_kelud_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

cols = ["user", "waktu", "review", "label"]
if show_pred and "prediksi_model" in df_view.columns:
    cols.append("prediksi_model")

df_display = df_view[cols].copy()

# Row styling dengan skema warna flat monokrom minimalis
def style_sentimen_rows(val):
    if val == "positif":
        return "background-color: #f0fdf4; color: #166534; font-weight: 600; font-size: 11px;"
    elif val == "negatif":
        return "background-color: #fef2f2; color: #991b1b; font-weight: 600; font-size: 11px;"
    return ""

styled_df = df_display.style.applymap(
    style_sentimen_rows,
    subset=[c for c in ["label", "prediksi_model"] if c in df_display.columns]
)

st.dataframe(styled_df, use_container_width=True, height=350)
st.caption(f"Query Result: {len(df_view):,} rows matches out of {len(df):,} records.")