import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

TODAY = datetime.date.today()
today_day = TODAY.strftime('%Y-%m-%d')

st.set_page_config(layout="wide", page_title="Natural Gas Analysis")

# ---------- Data Loading ----------
DATA_PATH = Path(__file__).resolve().parent / "datas" / "dash_storage.h5"

@st.cache_data(show_spinner=False)
def load_data(path: Path):
    comcot = pd.read_hdf(path, key='natgas_cots')
    natgas = pd.read_hdf(path, key='natgas')
    try:
        comcot.index = comcot.index.set_levels(
            pd.to_datetime(comcot.index.levels[1], format="%Y-%m-%d"),
            level=1
        )
    except Exception:
        pass
    return comcot, natgas

if not DATA_PATH.exists():
    st.error(f"Data file not found: {DATA_PATH}. Please add the HDF5 file to 'datas/' directory.")
    st.stop()

try:
    comcot_reports, natgas_yf = load_data(DATA_PATH)
except Exception as e:
    st.exception(e)
    st.stop()

# ---------- Date Bounds ----------
com_starting_date = natgas_yf.index.min()
com_ending_date = natgas_yf.index.max()

# ---------- Styling (Bright Background) ----------
page_bg_css = """
<style>
/* Force bright background across container & blocks */
[data-testid="stAppViewContainer"] > .main,
body, .block-container, .stApp, .stMain {
    background: #F5DEB3 !important;
    background-color: #F5DEB3 !important;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0) !important;
}

.stTabs [data-testid="stMarkdownContainer"] p {
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 1.5rem;
    font: "serif";
}

[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(to bottom, #BDB76B 0%, #B8860B 100%) !important;
    background-position: top left;
    background-attachment: fixed;
}

/* Remove any theme-imposed dark backgrounds */
section.main > div { background: transparent !important; }

/* Tighten default padding selectors may change per Streamlit versions */
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# Extra padding adjustments (hashed class names may change in future versions)
st.markdown("""
<style>
    .css-18e3th9 {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .css-1d391kg {
        padding-top: 0rem;
        padding-right: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Asset Resolver ----------
def _resolve_asset(*relative_segments: str):
    candidates = [
        Path(__file__).resolve().parent.joinpath(*relative_segments),
        Path.cwd().joinpath(*relative_segments),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

logo_path = _resolve_asset("datas", "logo1.png") or _resolve_asset("logo1.png")
if logo_path:
    st.sidebar.image(str(logo_path))
else:
    st.sidebar.warning("Logo not found (datas/logo1.png). Proceeding without it.")

# ---------- Sidebar Inputs ----------
col_from_to = st.sidebar.columns((1, 1))
with col_from_to[0]:
    start_nat = st.date_input(
        label="**FROM**",
        value=pd.to_datetime("2019-01-31", format="%Y-%m-%d"),
        label_visibility="collapsed"
    )
with col_from_to[1]:
    end_nat = st.date_input(
        label="**TO**",
        value=pd.to_datetime(today_day),
        label_visibility="collapsed"
    )

natgas_close = natgas_yf["Close"]
commodity = st.sidebar.selectbox(
    "**COM TICKER**",
    comcot_reports.index.get_level_values("ticker").unique(),
    label_visibility="collapsed"
)
com_columns = st.sidebar.selectbox(
    "**COT Ind full**",
    comcot_reports.columns,
    label_visibility="collapsed"
)

# ---------- Chart 1: NatGas Price + COT ----------
fig101 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.50, 0.50]
)

start_time_nat = pd.to_datetime(start_nat, format="%Y-%m-%d")
end_time_nat = pd.to_datetime(end_nat, format="%Y-%m-%d")
mask_natgas = (natgas_close.index < str(end_time_nat)) & (natgas_close.index >= str(start_time_nat))
subset_natgas = natgas_close.loc[mask_natgas]

fig101.add_trace(
    go.Scatter(
        x=subset_natgas.index,
        y=subset_natgas,
        fill='tozeroy',
        line=dict(color='black', width=1),
        name="NATGAS"
    ),
    row=1, col=1
)

max_close_nat = subset_natgas.max()
min_close_nat = subset_natgas.min()
fig101.update_layout(yaxis_range=[min_close_nat, max_close_nat], uniformtext_minsize=12)
fig101.add_annotation(
    text="NatGas Price",
    xref="paper", yref="paper",
    font=dict(size=30, color="#050303"), opacity=0.5,
    x=0.0, y=1.1, showarrow=False
)

# ---------- Chart 2: COT Series ----------
cot_commodity = comcot_reports.loc[commodity]
final_com = cot_commodity[com_columns]
max_diff = final_com.max()
min_diff = final_com.min()

fig101.add_trace(
    go.Scatter(
        x=final_com.index,
        y=final_com,
        fill='tonexty',
        name=" ",
        mode='lines',
        line=dict(color='#403824', width=1)
    ),
    row=2, col=1
)

fig101.update_yaxes(range=[min_diff, max_diff], row=2, col=1)
fig101.update_xaxes(range=[start_time_nat, end_time_nat])
fig101.update_layout(showlegend=False)
fig101.add_annotation(
    text="Commercial Activity",
    xref="paper", yref="paper",
    font=dict(size=30, color="#050303"), opacity=0.5,
    x=0.0, y=0.45, showarrow=False
)

fig101.update_traces(hovertemplate="%{x|%Y-%m-%d}", hoverinfo="skip")
fig101.update_layout(
    hoverlabel=dict(
        bgcolor='rgba(0,0,0,0)',
        font_size=10,
        font_color='rgba(0,0,0,10)',
        font_family="Ariel"
    )
)

# Transparent plot backgrounds so page color shows through
fig101.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    hovermode="x unified",
    height=1000,
    margin=dict(l=40, r=40, t=40, b=40)
)

fig101.for_each_xaxis(lambda x: x.update(showgrid=False))
fig101.for_each_yaxis(lambda x: x.update(showgrid=False))

# Use container width for true responsiveness and override Plotly chart CSS to force 90vw
st.markdown('<style>.element-container .js-plotly-plot {width:98vw !important; min-width:1000px; margin:auto;}</style>', unsafe_allow_html=True)
st.plotly_chart(fig101, use_container_width=True)

#############




