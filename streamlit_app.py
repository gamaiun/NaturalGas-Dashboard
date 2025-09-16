import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
TODAY = datetime.date.today()
today_day = TODAY.strftime('%Y-%m-%d')

st.set_page_config(layout="wide", page_title="Natural Gas Analysis")

##########  CREATING DATASETS ###############
DATA_PATH = Path(__file__).resolve().parent / "datas" / "dash_storage.h5"

@st.cache_data(show_spinner=False)
def load_data(path: Path):
    """Load HDF datasets and return (comcot_reports, natgas_yf).

    Uses caching to avoid re-reading large files on every interaction.
    """
    comcot = pd.read_hdf(path, key='natgas_cots')
    natgas = pd.read_hdf(path, key='natgas')
    # Ensure second level of MultiIndex is datetime for consistent filtering
    try:
        comcot.index = comcot.index.set_levels(pd.to_datetime(comcot.index.levels[1], format="%Y-%m-%d"), level=1)
    except Exception:
        # If already datetime or structure changes, silently continue
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

com_starting_date = natgas_yf.index.min()
com_ending_date = natgas_yf.index.max()


# Static bright background (#F5DEB3) and matching sidebar gradient
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] > .main {
background: #F5DEB3;
background-position: top left;
}

[data-testid="stHeader"] {
background: rgba(0,0,0,0);
}

.stTabs [data-testid="stMarkdownContainer"] p {
 background-color:transparent}

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.5rem;
    font:"serif";
    }

[data-testid="stSidebar"] >  div:first-child {
background: linear-gradient(to bottom, #BDB76B 0%, #B8860B 100%); 
background-position: top left;
background-attachment: fixed;
}

[data-testid="st.tabs"] >  div:first-child {
}

</style>
"""

st.markdown(  """
  <style>
  .css-16idsys.e16nr0p34 {
    background-color: #A0BFE0; 
            
    
  }
  </style>
""", unsafe_allow_html=True)

#side bar
def _resolve_asset(*relative_segments: str):
    """Return a Path to an existing asset trying several base folders."""
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
st.markdown(page_bg_img, unsafe_allow_html=True)

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
                        padding-bottom: 0rem;s
                        padding-left: 1rem;
                    }
            </style>
        """, unsafe_allow_html=True)


css = """
<style>
    .stTabs [data-baseweb="tab-highlight"] {
        background-color:transparent;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)




column = st.sidebar.columns((1, 1))



with column[0]:
    start_nat = st.date_input(label="**FROM**", value=pd.to_datetime("2019-01-31", format="%Y-%m-%d"), label_visibility="collapsed")
with column[1]:
    end_nat = st.date_input(label="**TO**", value=pd.to_datetime(today_day, ), label_visibility="collapsed")


natgas_close = natgas_yf["Close"]
commodity = st.sidebar.selectbox("**COM TICKER**", (comcot_reports.index.get_level_values("ticker").unique()), label_visibility="collapsed")
com_columns = st.sidebar.selectbox("**COT Ind full**", comcot_reports.columns, label_visibility="collapsed")

############# NATGAS CLOSE PRICE CHART #################

fig101 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.50, 0.50])
start_time_nat = pd.to_datetime(start_nat, format="%Y-%m-%d")
end_time_nat = pd.to_datetime(end_nat, format="%Y-%m-%d")
mask_natgas = (natgas_close.index < str(end_time_nat)) & (natgas_close.index >= str(start_time_nat))
subset_natgas = natgas_close.loc[mask_natgas]
fig101.add_trace(go.Scatter(x=subset_natgas.index, 
                            y=subset_natgas,
                            fill='tozeroy', 
                            line=dict(color='black', width=1), 
                            name="NATGAS"), 
                            row=1, col=1)


max_close_nat = natgas_close.loc[mask_natgas].max()
min_close_nat = natgas_close.loc[mask_natgas].min()
fig101.update_layout(yaxis_range=[min_close_nat, max_close_nat, ], uniformtext_minsize=12)
fig101.add_annotation(text=f"NatGas Price",
                       xref="paper", yref="paper", font=dict(size=30, color="#050303"), opacity=0.5,
                       x=0.0, y=1.1, showarrow=False)



    ########## PLOT COT REPORT #############

cot_commodity = comcot_reports.loc[commodity]
subset_cot_commodity = cot_commodity
final_com = subset_cot_commodity[com_columns]

max_diff = final_com.max()
min_diff = final_com.min()

fig101.add_trace(go.Scatter(x=final_com.index, 
                            y=final_com, 
                            fill='tonexty', 
                            name=" ", mode='lines', #line_color='blue',
                            line=dict(color='#403824', width=1)), 
                            row=2, col=1)

fig101.update_yaxes(range=[min_diff, max_diff], row=2, col=1)
fig101.update_xaxes(range=[start_time_nat, end_time_nat])
fig101.update_layout(showlegend=False)
fig101.add_annotation(text=f"Commercial Activity",
                       xref="paper", yref="paper", font=dict(size=30, color="#050303"), opacity=0.5,
                       x=0.0, y=0.45, showarrow=False)
fig101.update_traces(hovertemplate="%{x|%Y-%m-%d}", hoverinfo="skip")
fig101.update_layout(
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0)',
            font_size=10,
            font_color='rgba(0,0,0,10)',
            font_family="Ariel"))
fig101.update_traces(xaxis='x1')
fig101.update_layout(paper_bgcolor='rgb(184, 247, 212)', plot_bgcolor='rgb(184, 247, 212)')
fig101.update_layout(  paper_bgcolor='rgb(0,0,0,0)', 
                        plot_bgcolor='rgb(0,0,0,0)' )
fig101.update_layout(  hovermode="x unified", 
                        height = 1000,
                        margin=dict(l=40,r=40,t=40,b=40)  )
fig101.update_traces(  xaxis='x1'  )

fig101.for_each_xaxis(lambda x: x.update(showgrid=False))
fig101.for_each_yaxis(lambda x: x.update(showgrid=False))
st.plotly_chart(fig101, use_container_width=True)

#############




