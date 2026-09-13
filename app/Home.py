import sys
from pathlib import Path
# Ensure the project root is always on the Python path so that
# `core.*`, `app.*`, and `ingestion.*` imports resolve correctly
# regardless of the working directory Streamlit uses.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
from core.queries import get_stats_overview, get_incidents_by_year
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DB_PATH = _PROJECT_ROOT / "data" / "incidents.db"

if not _DB_PATH.exists():
    st.info("⏳ First run: fetching and building database (~60 seconds)...")
    from ingestion.run_pipeline import run_pipeline
    run_pipeline()
    st.rerun()


st.set_page_config(
    page_title="AI Incident Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
render_global_sidebar()


# ─── Streamlit-cached wrappers around pure query functions ───
@st.cache_data(ttl=3600)
def _cached_stats_overview(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_stats_overview(filters)

@st.cache_data(ttl=3600)
def _cached_incidents_by_year(filter_key=None):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    return get_incidents_by_year(filters)


# Custom CSS for polished aesthetic
st.markdown("""
<style>
    .reportview-container {
        background: #fafafa;
    }
    .metric-card {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 24px;
        text-align: center;
        border-top: 4px solid #F63366;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.95rem;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 AI Incident Analytics")
st.markdown("Explore and analyze data from the open **AIAAIC** (AI, Algorithmic, and Automation Incidents and Controversies) repository.")
st.markdown("___")

stats = _cached_stats_overview(_hashable_filters(get_current_filters()))

if stats is not None:
    # Stat Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total_incidents"]:,}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["min_year"]} - {stats["max_year"]}</div><div class="metric-label">Date Range</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["top_sector"]}</div><div class="metric-label">Top Sector</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["top_harm_type"]}</div><div class="metric-label">Leading Harm</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Headline Chart
    st.subheader("📈 Incidents Over Time")
    df_year = _cached_incidents_by_year(_hashable_filters(get_current_filters()))
    if not df_year.empty:
        fig = px.bar(df_year, x="year", y="count", 
                     title="Reported Incidents Volume (Annual)",
                     labels={"year": "Year", "count": "Incident Count"},
                     color_discrete_sequence=["#F63366"],
                     template="plotly_white")
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="",
            yaxis_title="# Incidents"
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No incidents match these filters.")
