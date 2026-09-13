import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from core.queries import get_stats_by_country
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

st.set_page_config(page_title="Geography", page_icon="🌍", layout="wide")

@st.cache_data(ttl=3600)
def _cached_stats_by_country(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_stats_by_country(filters)

render_global_sidebar()


st.title("🌍 Geographic Distribution")
st.markdown("Global heatmap of AI impacts based on identified country codes.")
st.markdown("___")

df = _cached_stats_by_country(_hashable_filters(get_current_filters()))

if df is not None and not df.empty:
    fig = px.choropleth(
        df,
        locations="iso_code",
        color="count",
        hover_name="name",
        color_continuous_scale="Reds",
        title="Global Incident Frequency"
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="equirectangular"),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Data Table")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No incidents match these filters.")
