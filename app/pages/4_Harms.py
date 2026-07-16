import streamlit as st
import plotly.express as px
from core.queries import get_stats_by_harm_type, get_sector_harm_matrix
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

st.set_page_config(page_title="Harm Types", page_icon="⚠️", layout="wide")

@st.cache_data(ttl=3600)
def _cached_stats_by_harm(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_stats_by_harm_type(filters)

@st.cache_data(ttl=3600)
def _cached_matrix(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_sector_harm_matrix(filters)

render_global_sidebar()


st.title("⚠️ Harm Types & Intersections")
st.markdown("Analyze the types of harm reported and how they intersect with various sectors.")
st.markdown("___")

df_harms = _cached_stats_by_harm(_hashable_filters(get_current_filters()))

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("Harm Type Distribution")
    if df_harms is not None and not df_harms.empty:
        fig_harms = px.pie(df_harms.head(15), names='harm_type', values='count', hole=0.4,
                           template="plotly_white", color_discrete_sequence=px.colors.sequential.YlOrRd[::-1])
        fig_harms.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_harms, use_container_width=True)
    else:
        st.warning("No incidents match these filters.")

with c2:
    st.subheader("Sector x Harm Heatmap")
    df_matrix = _cached_matrix(_hashable_filters(get_current_filters()))
    if df_matrix is not None and not df_matrix.empty:
        # Pivot the data for the heatmap
        pivot_df = df_matrix.pivot(index='harm_type', columns='sector', values='count').fillna(0)
        
        # Sort by total row and col sum for better visualization
        pivot_df = pivot_df.loc[pivot_df.sum(axis=1).sort_values(ascending=False).index]
        pivot_df = pivot_df[pivot_df.sum(axis=0).sort_values(ascending=False).index]
        
        # Limit to top 15x15 to keep it readable
        pivot_df = pivot_df.iloc[:15, :15]

        fig_heat = px.imshow(
            pivot_df, 
            text_auto=True, 
            aspect="auto",
            color_continuous_scale="Reds",
            labels=dict(x="Sector", y="Harm Type", color="Incidents")
        )
        fig_heat.update_xaxes(tickangle=-45)
        fig_heat.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("No incidents match these filters.")
