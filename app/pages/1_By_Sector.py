import streamlit as st
import plotly.express as px
from core.queries import get_stats_by_sector
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

st.set_page_config(page_title="By Sector", page_icon="🏭", layout="wide")

render_global_sidebar()


# Streamlit-cached wrapper
@st.cache_data(ttl=3600)
def _cached_stats_by_sector(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_stats_by_sector(filters)


st.title("🏭 Sector Analysis")
st.markdown("Breakdown of AI incidents by affected industry sectors.")
st.markdown("___")

df = _cached_stats_by_sector(_hashable_filters(get_current_filters()))

if df is not None and not df.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribution (Top 15)")
        top_15 = df.head(15)
        fig_pie = px.pie(top_15, names='sector', values='count', hole=0.4, 
                         template="plotly_white", color_discrete_sequence=px.colors.sequential.Sunset_r)
        fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.subheader("Top Sectors by Volume")
        fig_bar = px.bar(df.head(20), x='count', y='sector', orientation='h',
                         template="plotly_white", color_discrete_sequence=["#F63366"])
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0),
                              xaxis_title="Incident Count", yaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("No incidents match these filters.")
