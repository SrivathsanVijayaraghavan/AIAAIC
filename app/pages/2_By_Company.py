import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from core.queries import get_stats_by_company
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

st.set_page_config(page_title="By Company", page_icon="🏢", layout="wide")

# Streamlit-cached app-layer wrappers
@st.cache_data(ttl=3600)
def _cached_stats_by_company(role=None, filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_stats_by_company(role, filters)
render_global_sidebar()


st.title("🏢 Company Analysis")
st.markdown("Breakdown of AI incidents by involved organizations.")
st.markdown("___")

tab1, tab2, tab3 = st.tabs(["All Roles", "Deployers", "Developers"])

with tab1:
    df_all = _cached_stats_by_company(filter_key=_hashable_filters(get_current_filters()))
    if df_all is not None and not df_all.empty:
        fig1 = px.bar(df_all.head(20), x='count', y='company', orientation='h',
                      title="Top 20 Organizations Involved in Incidents",
                      template="plotly_white", color_discrete_sequence=["#F63366"])
        fig1.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=40, b=0),
                           xaxis_title="Incident Count", yaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No incidents match these filters.")

with tab2:
    df_deployer = _cached_stats_by_company(role="Deployer", filter_key=_hashable_filters(get_current_filters()))
    if df_deployer is not None and not df_deployer.empty:
        fig2 = px.bar(df_deployer.head(20), x='count', y='company', orientation='h',
                      title="Top 20 Deployers",
                      template="plotly_white", color_discrete_sequence=["#3b82f6"])
        fig2.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=40, b=0),
                           xaxis_title="Incident Count", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    df_dev = _cached_stats_by_company(role="Developer", filter_key=_hashable_filters(get_current_filters()))
    if df_dev is not None and not df_dev.empty:
        fig3 = px.bar(df_dev.head(20), x='count', y='company', orientation='h',
                      title="Top 20 Developers",
                      template="plotly_white", color_discrete_sequence=["#10b981"])
        fig3.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=40, b=0),
                           xaxis_title="Incident Count", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)
