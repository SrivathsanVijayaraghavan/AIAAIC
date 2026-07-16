import streamlit as st
import plotly.express as px
from core.queries import get_yoy_sector_trends, get_yoy_harm_trends
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

st.set_page_config(page_title="YoY Compare", page_icon="📈", layout="wide")

@st.cache_data(ttl=3600)
def _cached_yoy_sectors(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_yoy_sector_trends(filters)

@st.cache_data(ttl=3600)
def _cached_yoy_harms(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_yoy_harm_trends(filters)

render_global_sidebar()


st.title("📈 Year-over-Year Trends")
st.markdown("Analyze how the distribution of impacted sectors and harms shifts across time.")
st.markdown("___")

st.info("💡 **Note:** Data for the current calendar year is actively accumulating and may appear as an artificial drop-off compared to previous fully completed years.")

tab1, tab2 = st.tabs(["Sector Trends", "Harm Trends"])

with tab1:
    df_sec = _cached_yoy_sectors(_hashable_filters(get_current_filters()))
    if df_sec is not None and not df_sec.empty:
        # Keep the top 5 sectors overall for cleaner visualization
        top_sectors = df_sec.groupby('sector')['count'].sum().nlargest(5).index
        df_sec_top = df_sec[df_sec['sector'].isin(top_sectors)]
        
        fig_sec = px.line(df_sec_top, x="year", y="count", color="sector", markers=True,
                          title="Top 5 Sectors Over Time", template="plotly_white")
        fig_sec.update_layout(xaxis_title="Year", yaxis_title="Incident Count")
        st.plotly_chart(fig_sec, use_container_width=True)
    else:
        st.warning("No incidents match these filters.")

with tab2:
    df_harm = _cached_yoy_harms(_hashable_filters(get_current_filters()))
    if df_harm is not None and not df_harm.empty:
        top_harms = df_harm.groupby('harm_type')['count'].sum().nlargest(5).index
        df_harm_top = df_harm[df_harm['harm_type'].isin(top_harms)]

        fig_harm = px.bar(df_harm_top, x="year", y="count", color="harm_type",
                          title="Top 5 Harms Growth", template="plotly_white", barmode="group")
        fig_harm.update_layout(xaxis_title="Year", yaxis_title="Incident Count")
        st.plotly_chart(fig_harm, use_container_width=True)
    else:
        st.warning("No incidents match these filters.")
