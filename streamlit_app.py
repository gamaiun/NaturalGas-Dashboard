import streamlit as st
# import matplotlib.pyplot as plt
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
TODAY = datetime.date.today()
today_day = TODAY.strftime('%Y-%m-%d')

st.set_page_config(layout="wide", page_title="Natural Gas Analysis")

##########  CREATING DATASETS ###############
comcot_reports = pd.read_hdf('./datas/dash_storage.h5', key='natgas_cots',)
natgas_yf = pd.read_hdf('./datas/dash_storage.h5', key='natgas', )
comcot_reports.index = comcot_reports.index.set_levels(pd.to_datetime(comcot_reports.index.levels[1], format="%Y-%m-%d"), level=1)
com_starting_date = natgas_yf.index.min()
com_ending_date = natgas_yf.index.max()
com_date_range = pd.date_range(com_starting_date, com_ending_date)


page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background: linear-gradient(to bottom, #F5DEB3 0%,#F4A460 100%);
background-position: top left;
}}

        
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

.stTabs [data-testid="stMarkdownContainer"] p {{
 background-color:"green"}}

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
    font-size:1.5rem;
    font:"serif";
    }}

[data-testid="stSidebar"] >  div:first-child {{
background: linear-gradient(to bottom, #BDB76B  0%,#B8860B  100%); 
background-position: top left;
background-attachment: fixed;
}}

[data-testid="st.tabs"] >  div:first-child {{
<h3></h3>
}}

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
st.sidebar.image("datas/logo1.png")
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
                        height = 1000  )
fig101.update_traces(  xaxis='x1'  )

fig101.for_each_xaxis(lambda x: x.update(showgrid=False))
fig101.for_each_yaxis(lambda x: x.update(showgrid=False))
st.plotly_chart(fig101, use_container_width=True)

#############




